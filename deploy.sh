#!/bin/bash

# =================================================================
# 🚀 Deployment Script for Task Manager
# =================================================================

set -e  # Выход при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация
PROJECT_NAME="task-manager"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="/opt/backups/${PROJECT_NAME}"
LOG_DIR="/var/log/${PROJECT_NAME}"

echo -e "${BLUE}🚀 Deployment Script for ${PROJECT_NAME}${NC}"
echo "=================================================="

# Проверка прав суперпользователя
check_sudo() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}❌ Этот скрипт должен запускаться с правами sudo${NC}"
        echo "Использование: sudo ./deploy.sh"
        exit 1
    fi
}

# Проверка зависимостей
check_dependencies() {
    echo -e "${YELLOW}🔍 Проверка зависимостей...${NC}"
    
    # Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker не установлен${NC}"
        echo "Установите Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose не установлен${NC}"
        echo "Установите Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ Git не установлен${NC}"
        echo "Установите Git: apt update && apt install -y git"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Все зависимости установлены${NC}"
}

# Создание необходимых директорий
create_directories() {
    echo -e "${YELLOW}📁 Создание директорий...${NC}"
    
    mkdir -p "${BACKUP_DIR}"
    mkdir -p "${LOG_DIR}"
    mkdir -p "/opt/${PROJECT_NAME}/data"
    mkdir -p "/opt/${PROJECT_NAME}/ssl"
    
    echo -e "${GREEN}✅ Директории созданы${NC}"
}

# Настройка firewall
setup_firewall() {
    echo -e "${YELLOW}🔥 Настройка firewall...${NC}"
    
    # Устанавливаем ufw если не установлен
    if ! command -v ufw &> /dev/null; then
        apt update && apt install -y ufw
    fi
    
    # Базовые правила
    ufw --force enable
    ufw default deny incoming
    ufw default allow outgoing
    
    # SSH
    ufw allow ssh
    
    # HTTP/HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Application port (если нужен прямой доступ)
    # ufw allow 4000/tcp
    
    echo -e "${GREEN}✅ Firewall настроен${NC}"
}

# Установка Docker
install_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}🐳 Установка Docker...${NC}"
        
        # Удаляем старые версии
        apt remove -y docker docker-engine docker.io containerd runc
        
        # Устанавливаем зависимости
        apt update
        apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
        
        # Добавляем GPG ключ Docker
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        # Добавляем репозиторий
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Устанавливаем Docker
        apt update
        apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        
        # Запускаем Docker
        systemctl start docker
        systemctl enable docker
        
        echo -e "${GREEN}✅ Docker установлен${NC}"
    fi
}

# Проверка .env файла
check_env_file() {
    echo -e "${YELLOW}🔍 Проверка .env файла...${NC}"
    
    if [[ ! -f ".env" ]]; then
        echo -e "${RED}❌ Файл .env не найден${NC}"
        echo "Создайте .env файл на основе env.production.example"
        echo "cp env.production.example .env"
        echo "Затем отредактируйте его со своими настройками"
        exit 1
    fi
    
    # Проверяем обязательные переменные
    if ! grep -q "SECRET_KEY=" .env || grep -q "your-super-secret-key-change-this" .env; then
        echo -e "${RED}❌ Измените SECRET_KEY в .env файле!${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ .env файл настроен${NC}"
}

# Резервное копирование
backup_current() {
    if [[ -d "/opt/${PROJECT_NAME}" ]]; then
        echo -e "${YELLOW}💾 Создание резервной копии...${NC}"
        
        BACKUP_NAME="${PROJECT_NAME}_backup_$(date +%Y%m%d_%H%M%S)"
        tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" -C "/opt" "${PROJECT_NAME}"
        
        echo -e "${GREEN}✅ Резервная копия создана: ${BACKUP_NAME}.tar.gz${NC}"
    fi
}

# Развертывание приложения
deploy_application() {
    echo -e "${YELLOW}🚀 Развертывание приложения...${NC}"
    
    # Переходим в рабочую директорию
    cd "/opt/${PROJECT_NAME}"
    
    # Останавливаем существующие контейнеры
    if [[ -f "${DOCKER_COMPOSE_FILE}" ]]; then
        docker-compose -f "${DOCKER_COMPOSE_FILE}" down
    fi
    
    # Копируем файлы проекта (предполагается, что они уже в текущей директории)
    # В реальном деплое здесь будет git clone или копирование файлов
    
    # Собираем и запускаем контейнеры
    docker-compose -f "${DOCKER_COMPOSE_FILE}" up -d --build
    
    echo -e "${GREEN}✅ Приложение развернуто${NC}"
}

# Проверка здоровья сервисов
health_check() {
    echo -e "${YELLOW}🏥 Проверка здоровья сервисов...${NC}"
    
    # Ждем запуска сервисов
    sleep 30
    
    # Проверяем статус контейнеров
    if docker-compose -f "${DOCKER_COMPOSE_FILE}" ps | grep -q "Up"; then
        echo -e "${GREEN}✅ Сервисы запущены${NC}"
    else
        echo -e "${RED}❌ Проблемы с запуском сервисов${NC}"
        docker-compose -f "${DOCKER_COMPOSE_FILE}" logs
        exit 1
    fi
    
    # Проверяем HTTP ответ
    if curl -f http://localhost:4000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API отвечает${NC}"
    else
        echo -e "${RED}❌ API не отвечает${NC}"
        exit 1
    fi
}

# Настройка логирования
setup_logging() {
    echo -e "${YELLOW}📝 Настройка логирования...${NC}"
    
    # Логротация
    cat > /etc/logrotate.d/${PROJECT_NAME} << EOF
/var/log/${PROJECT_NAME}/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF
    
    echo -e "${GREEN}✅ Логирование настроено${NC}"
}

# Настройка системного сервиса
setup_systemd_service() {
    echo -e "${YELLOW}⚙️ Настройка системного сервиса...${NC}"
    
    cat > /etc/systemd/system/${PROJECT_NAME}.service << EOF
[Unit]
Description=${PROJECT_NAME} Docker Compose Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/${PROJECT_NAME}
ExecStart=/usr/bin/docker-compose -f ${DOCKER_COMPOSE_FILE} up -d
ExecStop=/usr/bin/docker-compose -f ${DOCKER_COMPOSE_FILE} down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable ${PROJECT_NAME}.service
    
    echo -e "${GREEN}✅ Системный сервис настроен${NC}"
}

# Показать итоговую информацию
show_summary() {
    echo ""
    echo -e "${GREEN}🎉 Развертывание завершено успешно!${NC}"
    echo "=================================================="
    echo -e "${BLUE}📊 Информация о сервисах:${NC}"
    echo "  • Веб-приложение: http://your-server-ip:4000"
    echo "  • API документация: http://your-server-ip:4000/docs"
    echo "  • Логи приложения: ${LOG_DIR}"
    echo "  • Резервные копии: ${BACKUP_DIR}"
    echo ""
    echo -e "${BLUE}🔧 Полезные команды:${NC}"
    echo "  • Статус сервисов: systemctl status ${PROJECT_NAME}"
    echo "  • Перезапуск: systemctl restart ${PROJECT_NAME}"
    echo "  • Логи: docker-compose -f ${DOCKER_COMPOSE_FILE} logs -f"
    echo "  • Остановка: systemctl stop ${PROJECT_NAME}"
    echo ""
    echo -e "${YELLOW}⚠️ Следующие шаги:${NC}"
    echo "  1. Настройте SSL сертификаты"
    echo "  2. Настройте доменное имя"
    echo "  3. Настройте мониторинг"
    echo "  4. Настройте регулярные бэкапы"
    echo ""
}

# Основная функция
main() {
    case "${1:-deploy}" in
        "install")
            check_sudo
            install_docker
            setup_firewall
            create_directories
            ;;
        "deploy")
            check_sudo
            check_dependencies
            check_env_file
            backup_current
            deploy_application
            health_check
            setup_logging
            setup_systemd_service
            show_summary
            ;;
        "backup")
            backup_current
            ;;
        "logs")
            docker-compose -f "${DOCKER_COMPOSE_FILE}" logs -f
            ;;
        "status")
            docker-compose -f "${DOCKER_COMPOSE_FILE}" ps
            ;;
        "restart")
            docker-compose -f "${DOCKER_COMPOSE_FILE}" restart
            ;;
        "stop")
            docker-compose -f "${DOCKER_COMPOSE_FILE}" down
            ;;
        "update")
            check_sudo
            backup_current
            docker-compose -f "${DOCKER_COMPOSE_FILE}" pull
            docker-compose -f "${DOCKER_COMPOSE_FILE}" up -d
            health_check
            ;;
        *)
            echo "Использование: $0 {install|deploy|backup|logs|status|restart|stop|update}"
            echo ""
            echo "Команды:"
            echo "  install  - Установка Docker и настройка системы"
            echo "  deploy   - Полное развертывание приложения"
            echo "  backup   - Создание резервной копии"
            echo "  logs     - Просмотр логов"
            echo "  status   - Статус сервисов"
            echo "  restart  - Перезапуск сервисов"
            echo "  stop     - Остановка сервисов"
            echo "  update   - Обновление приложения"
            exit 1
            ;;
    esac
}

# Запуск
main "$@" 