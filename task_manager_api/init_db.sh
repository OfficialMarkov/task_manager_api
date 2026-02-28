#!/bin/bash
# Скрипт для инициализации базы данных

echo "Создание начальной миграции..."
alembic revision --autogenerate -m "Initial migration"

echo "Применение миграций..."
alembic upgrade head

echo "База данных инициализирована!"
