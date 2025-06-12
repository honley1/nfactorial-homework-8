# ⚡ Быстрый деплой Task Manager

## 🚀 За 5 минут

### 1. Подготовка сервера Ubuntu
```bash
sudo ./server-setup.sh
```

### 2. Настройка переменных
```bash
cp env.production.example .env
nano .env
# Измените SECRET_KEY и ALLOWED_HOSTS
```

### 3. Деплой
```bash
sudo ./deploy.sh deploy
```

### 4. Проверка
```bash
curl http://your-ip:4000/api/health
# Откройте http://your-ip:4000 в браузере
```

## 🔧 Управление

```bash
# Статус
sudo docker-compose ps

# Логи
sudo docker-compose logs -f

# Перезапуск
sudo docker-compose restart

# Остановка
sudo docker-compose down

# Redis мониторинг
./redis_commands.sh queues
python3 redis_monitor.py
```

## 🆘 Если что-то не работает

```bash
# Пересборка всех контейнеров
sudo docker-compose down
sudo docker-compose up -d --build

# Проверка логов
sudo docker-compose logs task-manager
sudo docker-compose logs celery-worker
sudo docker-compose logs redis
```

## ✅ Готово!
- Веб-интерфейс: `http://your-ip:4000`
- API документация: `http://your-ip:4000/docs`
- Все функции работают: CRUD, JWT, Celery, Redis 