#!/bin/sh

ollama serve &

echo "Ждем запуск Ollama"

until ollama list >/dev/null 2>&1; do
    sleep 1
done

echo "Загружаем модель"

ollama pull qwen2.5:7b-instruct-q4_K_M

ollama run qwen2.5:7b-instruct-q4_K_M

wait