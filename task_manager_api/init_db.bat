@echo off
REM Скрипт для инициализации базы данных (Windows)

echo Создание начальной миграции...
alembic revision --autogenerate -m "Initial migration"

echo Применение миграций...
alembic upgrade head

echo База данных инициализирована!
pause
