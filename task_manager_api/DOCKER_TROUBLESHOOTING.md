# Решение проблем с Docker

## Проблема 1: Docker Desktop не запущен

**Ошибка:**
```
error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.51/...": 
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

**Решение:**
1. Запустите Docker Desktop на Windows
2. Дождитесь полной загрузки (иконка Docker в трее должна быть зеленая)
3. Проверьте, что Docker работает:
   ```powershell
   docker ps
   ```
   Если команда выполняется без ошибок - Docker запущен

## Проблема 2: SECRET_KEY не установлен

**Ошибка:**
```
level=warning msg="The \"SECRET_KEY\" variable is not set. Defaulting to a blank string."
```

**Решение:**
1. Создайте файл `.env` в корне проекта (если еще не создан):
   ```powershell
   Copy-Item env.example .env
   ```

2. Откройте `.env` и установите SECRET_KEY:
   ```env
   SECRET_KEY=ваш-случайный-ключ-минимум-32-символа
   ```

3. Сгенерируйте безопасный ключ:
   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

## Проблема 3: version в docker-compose.yml устарел

**Ошибка:**
```
level=warning msg="...docker-compose.yml: the attribute `version` is obsolete..."
```

**Решение:**
✅ Уже исправлено! Убрал `version: '3.8'` из docker-compose.yml

## Пошаговая инструкция запуска

### Шаг 1: Запустите Docker Desktop
- Откройте Docker Desktop
- Дождитесь полной загрузки

### Шаг 2: Создайте .env файл
```powershell
# В корне проекта
Copy-Item env.example .env
```

### Шаг 3: Установите SECRET_KEY в .env
Откройте `.env` и измените:
```env
SECRET_KEY=сгенерируйте-случайный-ключ-32-символа-минимум
```

### Шаг 4: Запустите Docker Compose
```powershell
docker-compose up -d
```

### Шаг 5: Примените миграции БД
```powershell
docker-compose exec api alembic upgrade head
```

### Шаг 6: Проверьте работу
Откройте в браузере: http://localhost:8000/docs

## Проверка статуса контейнеров

```powershell
# Посмотреть все контейнеры
docker-compose ps

# Посмотреть логи
docker-compose logs

# Посмотреть логи конкретного сервиса
docker-compose logs api
docker-compose logs db

# Остановить все контейнеры
docker-compose down

# Остановить и удалить volumes (БД будет очищена!)
docker-compose down -v
```

## Если Docker Desktop не устанавливается

1. Убедитесь, что включен WSL 2:
   ```powershell
   wsl --status
   ```

2. Если WSL 2 не установлен, установите его:
   ```powershell
   wsl --install
   ```

3. Перезагрузите компьютер после установки WSL 2

4. Установите Docker Desktop с официального сайта:
   https://www.docker.com/products/docker-desktop/
