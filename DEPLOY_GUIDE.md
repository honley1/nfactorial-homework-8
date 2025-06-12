# 🚀 Полное руководство по деплою Task Manager

## 📋 Что готово к деплою

✅ **FastAPI приложение** с JWT аутентификацией  
✅ **SQLite база данных** с готовыми моделями  
✅ **Redis** для Celery очередей  
✅ **Celery Worker + Beat** для асинхронных задач  
✅ **Docker + Docker Compose** конфигурация  
✅ **Nginx** reverse proxy с SSL поддержкой  
✅ **Автоматические скрипты** деплоя  
✅ **Мониторинг и логирование**  

---

## 🎯 Варианты деплоя

### 🚀 Вариант 1: Автоматический деплой (Рекомендуется)

#### Шаг 1: Подготовка сервера
```bash
# На новом Ubuntu сервере
sudo ./server-setup.sh
```

#### Шаг 2: Настройка окружения
```bash
# Копируем и редактируем конфигурацию
cp env.production.example .env
nano .env

# Обязательно измените:
# - SECRET_KEY=ваш-уникальный-секретный-ключ
# - ALLOWED_HOSTS=ваш-домен.com,ip-сервера
```

#### Шаг 3: Деплой
```bash
sudo ./deploy.sh deploy
```

**Готово!** Приложение будет доступно на `http://ваш-ip:4000`

---

### 🔧 Вариант 2: Ручной деплой

#### Шаг 1: Подготовка сервера
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo apt install docker-compose-plugin

# Настройка firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable
```

#### Шаг 2: Загрузка проекта
```bash
# Загрузите проект на сервер в /opt/task-manager
# Например, через git:
sudo git clone YOUR_REPO_URL /opt/task-manager
cd /opt/task-manager
```

#### Шаг 3: Настройка переменных
```bash
# Создание .env файла
sudo cp env.production.example .env
sudo nano .env

# Измените обязательные параметры:
SECRET_KEY=your-super-long-secret-key-here
ALLOWED_HOSTS=yourdomain.com,your-server-ip
```

#### Шаг 4: Запуск
```bash
# Создание директорий
sudo mkdir -p data ssl

# Запуск всех сервисов
sudo docker-compose up -d --build
```

---

## 🌐 Настройка домена и SSL

### Базовая настройка
```bash
# Проверка работы
curl http://ваш-ip:4000/api/health

# Если работает, настройте домен:
# 1. Направьте A-запись домена на IP сервера
# 2. Дождитесь распространения DNS (до 24 часов)
```

### SSL сертификаты (Let's Encrypt)
```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d yourdomain.com

# В nginx.conf раскомментируйте SSL строки и перезапустите
sudo docker-compose restart nginx
```

---

## 🔧 Управление сервисами

### Основные команды
```bash
# Статус сервисов
sudo docker-compose ps

# Логи
sudo docker-compose logs -f                    # Все сервисы
sudo docker-compose logs -f task-manager       # Только приложение
sudo docker-compose logs -f celery-worker      # Только Celery

# Перезапуск
sudo docker-compose restart

# Остановка
sudo docker-compose down

# Обновление
sudo docker-compose pull
sudo docker-compose up -d --build
```

### Мониторинг Redis и Celery
```bash
# Статус Redis
./redis_commands.sh status

# Очереди Celery
./redis_commands.sh queues

# Полный мониторинг
python3 redis_monitor.py
```

---

## 📊 Первый запуск

### 1. Создание администратора
```bash
# Подключитесь к контейнеру приложения
sudo docker exec -it task-manager-app-prod bash

# Создайте суперпользователя (если есть такая возможность)
# Или зарегистрируйтесь через веб-интерфейс
```

### 2. Проверка функциональности
- Откройте `http://ваш-ip:4000`
- Зарегистрируйте пользователя
- Создайте несколько задач
- Проверьте API документацию: `http://ваш-ip:4000/docs`

### 3. Тестирование Celery
```bash
# В интерфейсе создайте задачу
# Проверьте логи worker'а:
sudo docker-compose logs -f celery-worker

# Или через API:
curl -X POST http://ваш-ip:4000/api/celery/test-task \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🔒 Безопасность

### Обязательные настройки
```bash
# 1. Измените пароли по умолчанию
# 2. Настройте fail2ban
sudo systemctl status fail2ban

# 3. Обновите систему
sudo apt update && sudo apt upgrade -y

# 4. Настройте регулярные бэкапы
sudo crontab -e
# Добавьте: 0 2 * * * /opt/task-manager/deploy.sh backup
```

### Firewall правила
```bash
sudo ufw status
# Должны быть открыты только: 22 (SSH), 80 (HTTP), 443 (HTTPS)
```

---

## 📁 Структура на сервере

```
/opt/task-manager/
├── app/                    # Приложение FastAPI
├── data/                   # База данных SQLite
├── ssl/                    # SSL сертификаты
├── docker-compose.yml      # Конфигурация сервисов
├── nginx.conf             # Конфигурация Nginx
├── .env                   # Переменные окружения
└── deploy.sh              # Скрипт управления

/var/log/task-manager/      # Логи приложения
/opt/backups/task-manager/  # Резервные копии
```

---

## 🆘 Устранение проблем

### Приложение не запускается
```bash
# Проверьте логи
sudo docker-compose logs task-manager

# Проверьте .env файл
cat .env

# Пересоберите контейнеры
sudo docker-compose down
sudo docker-compose up -d --build
```

### Redis/Celery не работают
```bash
# Проверьте статус Redis
./redis_commands.sh ping

# Проверьте очереди
./redis_commands.sh queues

# Перезапустите Celery
sudo docker-compose restart celery-worker celery-beat
```

### Nginx ошибки
```bash
# Проверьте конфигурацию
sudo docker exec task-manager-nginx-prod nginx -t

# Логи Nginx
sudo docker-compose logs nginx
```

### Проблемы с SSL
```bash
# Проверьте сертификаты
sudo certbot certificates

# Обновите сертификаты
sudo certbot renew --dry-run
```

---

## 📈 Масштабирование

### Для увеличения нагрузки:
```bash
# Увеличьте количество Celery worker'ов
# В docker-compose.yml измените:
command: celery -A app.celery_app worker --loglevel=info --concurrency=4

# Добавьте больше worker контейнеров
# Настройте load balancer перед Nginx
```

---

## ✅ Checklist деплоя

- [ ] Сервер подготовлен (`server-setup.sh`)
- [ ] `.env` файл настроен (SECRET_KEY, ALLOWED_HOSTS)
- [ ] Домен направлен на сервер
- [ ] Приложение запущено (`docker-compose up -d`)
- [ ] Все сервисы работают (`docker-compose ps`)
- [ ] API отвечает (`curl http://ip:4000/api/health`)
- [ ] Можно войти в веб-интерфейс
- [ ] Celery обрабатывает задачи
- [ ] SSL сертификаты настроены
- [ ] Firewall настроен
- [ ] Бэкапы настроены

---

## 🎉 Готово!

Ваш Task Manager с Celery и Redis успешно развернут в продакшене!

**Адреса:**
- Веб-интерфейс: `https://yourdomain.com`
- API документация: `https://yourdomain.com/docs`
- Мониторинг: `python3 redis_monitor.py` 