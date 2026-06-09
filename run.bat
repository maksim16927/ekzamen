@echo off
chcp 65001 >nul
title Магазин игрушек - запуск

echo Установка зависимостей...
pip install -r requirements.txt

set TOYSTORE_USER=postgres
set /p TOYSTORE_PASSWORD=Введите пароль пользователя postgres:

echo Запуск приложения...
python main.py

pause
