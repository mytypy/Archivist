#!/bin/sh

ollama serve &

echo "Ждем запуск Ollama..."
until ollama list > /dev/null 2>&1; do
    sleep 1
done

if ! ollama list | grep -q "qwen2.5:7b-instruct-q4_K_M"; then
    echo "Модель не найдена, скачиваем..."
    ollama pull qwen2.5:7b-instruct-q4_K_M
else
    echo "Модель уже загружена, пропускаем pull"
fi

wait