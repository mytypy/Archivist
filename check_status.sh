#!/usr/bin/env bash

# Цвета для вывода
GREEN="\033[1;32m"
RED="\033[1;31m"
YELLOW="\033[1;33m"
CYAN="\033[1;36m"
BOLD="\033[1m"
DIM="\033[2m"
RESET="\033[0m"

# Очистка экрана и курсор при выходе
trap 'echo -e "\n${RESET}Мониторинг остановлен."; tput cnorm 2>/dev/null; exit 0' SIGINT SIGTERM

# Скрываем мигающий курсор для плавного дашборда
tput civis 2>/dev/null

DELAY=4
ONCE_MODE=false

if [ "$1" = "--once" ] || [ "$1" = "-1" ]; then
    ONCE_MODE=true
fi

check_container_status() {
    local name="$1"
    local status
    status=$(docker inspect -f '{{.State.Status}}' "$name" 2>/dev/null)
    echo "$status"
}

while true; do
    # Очистка экрана
    clear

    CURRENT_TIME=$(date "+%H:%M:%S")

    echo -e "${BOLD}${CYAN}================================================================${RESET}"
    echo -e "${BOLD}${CYAN}   Архивариус — Real-time мониторинг системы [${CURRENT_TIME}]    ${RESET}"
    echo -e "${BOLD}${CYAN}================================================================${RESET}"
    if [ "$ONCE_MODE" = false ]; then
        echo -e "${DIM}Опрос каждые ${DELAY} сек. Для выхода нажмите Ctrl+C${RESET}\n"
    else
        echo -e ""
    fi

    TOTAL_CHECKS=7
    PASSED_CHECKS=0

    # 1. Проверка контейнеров
    echo -e "${BOLD}1. Docker контейнеры:${RESET}"

    declare -A CONTAINERS=(
        ["archivist_db"]="PostgreSQL 17"
        ["archivist-redis"]="Redis (Valkey)"
        ["llm-model"]="Ollama Engine (GPU)"
        ["llm_service"]="AI-Service"
        ["backend_container"]="Backend API"
        ["bot_container"]="MAX Bot Webhook"
    )

    CONTAINER_ORDER=("archivist_db" "archivist-redis" "llm-model" "llm_service" "backend_container" "bot_container")

    for c in "${CONTAINER_ORDER[@]}"; do
        desc="${CONTAINERS[$c]}"
        status=$(check_container_status "$c")

        if [ "$status" = "running" ]; then
            printf "  %-30s [ %b ]\n" "$desc ($c)" "${GREEN}RUNNING${RESET}"
        elif [ -n "$status" ]; then
            printf "  %-30s [ %b ] (статус: %s)\n" "$desc ($c)" "${YELLOW}WAITING${RESET}" "$status"
        else
            printf "  %-30s [ %b ] (не запущен)\n" "$desc ($c)" "${RED}STOPPED${RESET}"
        fi
    done

    # 2. База данных и кэш
    echo -e "\n${BOLD}2. База данных и Redis:${RESET}"

    # PostgreSQL
    if docker exec archivist_db pg_isready -U postgres >/dev/null 2>&1; then
        printf "  %-30s [ %b ]\n" "PostgreSQL ready" "${GREEN}READY${RESET}"
        ((PASSED_CHECKS++))
    else
        printf "  %-30s [ %b ]\n" "PostgreSQL ready" "${RED}NOT READY${RESET}"
    fi

    # Redis PING
    REDIS_PING=$(docker exec archivist-redis redis-cli ping 2>/dev/null | tr -d '\r')
    if [ "$REDIS_PING" = "PONG" ]; then
        printf "  %-30s [ %b ]\n" "Redis ping (PONG)" "${GREEN}PONG${RESET}"
        ((PASSED_CHECKS++))
    else
        printf "  %-30s [ %b ]\n" "Redis ping" "${RED}NO PONG${RESET}"
    fi

    # 3. LLM и Модель
    echo -e "\n${BOLD}3. Локальная LLM (Qwen 2.5):${RESET}"

    OLLAMA_STATUS=$(check_container_status "llm-model")
    if [ "$OLLAMA_STATUS" = "running" ]; then
        if docker exec llm-model ollama list 2>/dev/null | grep -q "qwen2.5:7b-instruct-q4_K_M"; then
            printf "  %-30s [ %b ] (загружена в память)\n" "qwen2.5:7b-instruct-q4_K_M" "${GREEN}READY${RESET}"
            ((PASSED_CHECKS++))
        else
            printf "  %-30s [ %b ] (идёт скачивание/инициализация...)\n" "qwen2.5:7b-instruct-q4_K_M" "${YELLOW}PULLING${RESET}"
        fi
    else
        printf "  %-30s [ %b ]\n" "Ollama Container" "${RED}OFFLINE${RESET}"
    fi

    # 4. HTTP Healthchecks
    echo -e "\n${BOLD}4. Доступность API:${RESET}"

    # AI-Service
    AI_HTTP=$(docker exec llm_service python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health/', timeout=2).getcode())" 2>/dev/null | tr -d '\r')
    if [ "$AI_HTTP" = "200" ]; then
        printf "  %-30s [ %b ] (HTTP 200)\n" "AI-Service /health/" "${GREEN}ONLINE${RESET}"
        ((PASSED_CHECKS++))
    else
        printf "  %-30s [ %b ] (ожидание старта сервиса/модели)\n" "AI-Service /health/" "${YELLOW}OFFLINE${RESET}"
    fi

    # Backend
    BACKEND_HTTP=$(docker exec backend_container python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health/', timeout=2).getcode())" 2>/dev/null | tr -d '\r')
    if [ "$BACKEND_HTTP" = "200" ]; then
        printf "  %-30s [ %b ] (HTTP 200)\n" "Backend API /api/health/" "${GREEN}ONLINE${RESET}"
        ((PASSED_CHECKS++))
    else
        printf "  %-30s [ %b ] (ожидание старта API)\n" "Backend API /api/health/" "${YELLOW}OFFLINE${RESET}"
    fi

    # Bot
    BOT_STATUS=$(check_container_status "bot_container")
    if [ "$BOT_STATUS" = "running" ]; then
        printf "  %-30s [ %b ] (вебхук слушает порт)\n" "Bot Worker (MAX)" "${GREEN}ONLINE${RESET}"
        ((PASSED_CHECKS++))
    else
        printf "  %-30s [ %b ]\n" "Bot Worker (MAX)" "${RED}OFFLINE${RESET}"
    fi

    # 5. Итог
    echo -e "\n${BOLD}${CYAN}-------------------------------------------------------------------------------------${RESET}"
    if [ "$PASSED_CHECKS" -ge 6 ]; then
        echo -e "${BOLD}${GREEN}✔ ВСЕ СЕРВИСЫ УСПЕШНО ЗАПУЩЕНЫ И ГОТОВЫ К РАБОТЕ!${RESET} МОЖЕТЕ РАБОТАТЬ С БОТОМ"
    else
        echo -e "${BOLD}${YELLOW}⏳ Идёт запуск/прогрев сервисов (${PASSED_CHECKS}/6 готовы)...${RESET}"
        echo -e "${DIM}Логи: docker logs -f llm-model | docker logs -f llm_service${RESET}"
    fi
    echo -e "${BOLD}${CYAN}=======================================================================================${RESET}"

    if [ "$ONCE_MODE" = true ]; then
        tput cnorm 2>/dev/null
        exit 0
    fi

    sleep "$DELAY"
done
