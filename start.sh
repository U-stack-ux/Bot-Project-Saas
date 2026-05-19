#!/bin/bash
echo "🚀 Iniciando o Ecossistema HiveOS Monitor..."
termux-wake-lock
echo "✅ Wake Lock Ativado"

echo "🐹 Iniciando Backend em Go..."
cd ~/bot_monitoramento_project/bot_banked
go run . > backend.log 2>&1 &
sleep 3

echo "🐍 Iniciando Bot em Python..."
cd ~/bot_monitoramento_project/bot_discord
python bot.py
