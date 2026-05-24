#!/bin/bash

echo "⚙️  Modo de Teste Local..."

# 1. Compila o Go na raiz
echo "🚀 Compilando Go..."
go build -o server_bin *.go
if [ $? -ne 0 ]; then
    echo "❌ Erro ao compilar o Go."
    exit 1
fi

# 2. Executa o Bot (que por sua vez vai chamar o server_bin automaticamente)
echo "🚀 Iniciando ecossistema integrado..."
export PORT=8080
python3 bot.py
