#!/bin/bash

# =================================================================
# 🖥️ Server Setup Script for Task Manager
# Скрипт для первоначальной настройки сервера
# =================================================================

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_NAME="task-manager"
PROJECT_USER="taskmanager"
PROJECT_DIR="/opt/${PROJECT_NAME}"

echo -e "${BLUE}🖥️ Server Setup for ${PROJECT_NAME}${NC}"
echo "============================================="

# Проверка прав суперпользователя
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}❌ Этот скрипт должен запускаться с правами sudo${NC}"
    exit 1
fi

# Обновление системы
update_system() {
    echo -e "${YELLOW}📦 Обновление системы...${NC}"
    apt update && apt upgrade -y
    echo -e "${GREEN}✅ Система обновлена${NC}"
}

# Установка базовых пакетов
install_basic_packages() {
    echo -e "${YELLOW}📦 Установка базовых пакетов...${NC}"
    
    apt install -y \
        curl \
        wget \
        git \
        htop \
        nano \
        vim \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        ufw \
        fail2ban \
        certbot \
        python3-certbot-nginx
    
    echo -e "${GREEN}✅ Базовые пакеты установлены${NC}"
}

# Создание пользователя для проекта
create_project_user() {
    echo -e "${YELLOW}👤 Создание пользователя ${PROJECT_USER}...${NC}"
    
    if ! id "${PROJECT_USER}" &>/dev/null; then
        adduser --system --group --home "${PROJECT_DIR}" --shell /bin/bash "${PROJECT_USER}"
        usermod -aG docker "${PROJECT_USER}"
        echo -e "${GREEN}✅ Пользователь ${PROJECT_USER} создан${NC}"
    else
        echo -e "${YELLOW}⚠️ Пользователь ${PROJECT_USER} уже существует${NC}"
    fi
}

# Настройка SSH безопасности
setup_ssh_security() {
    echo -e "${YELLOW}🔐 Настройка SSH безопасности...${NC}"
    
    # Резервная копия конфигурации SSH
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    
    # Базовые настройки безопасности SSH
    sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
    
    # Перезапуск SSH
    systemctl restart ssh
    
    echo -e "${GREEN}✅ SSH безопасность настроена${NC}"
    echo -e "${YELLOW}⚠️ Убедитесь, что у вас есть SSH ключ перед отключением!${NC}"
}

# Настройка firewall
setup_advanced_firewall() {
    echo -e "${YELLOW}🔥 Настройка расширенного firewall...${NC}"
    
    # Базовые правила
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    
    # SSH
    ufw allow ssh
    
    # HTTP/HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Ограничение SSH соединений
    ufw limit ssh
    
    # Включение
    ufw --force enable
    
    echo -e "${GREEN}✅ Firewall настроен${NC}"
}

# Настройка Fail2Ban
setup_fail2ban() {
    echo -e "${YELLOW}🛡️ Настройка Fail2Ban...${NC}"
    
    # Конфигурация для SSH
    cat > /etc/fail2ban/jail.d/ssh.conf << 'EOF'
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
EOF
    
    # Конфигурация для Nginx (если используется)
    cat > /etc/fail2ban/jail.d/nginx.conf << 'EOF'
[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 10
bantime = 600
EOF
    
    systemctl enable fail2ban
    systemctl start fail2ban
    
    echo -e "${GREEN}✅ Fail2Ban настроен${NC}"
}

# Установка Docker
install_docker() {
    echo -e "${YELLOW}🐳 Установка Docker...${NC}"
    
    # Удаление старых версий
    apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Добавление репозитория Docker
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Установка
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Добавление пользователей в группу docker
    usermod -aG docker "${PROJECT_USER}"
    
    # Настройка автозапуска
    systemctl enable docker
    systemctl start docker
    
    echo -e "${GREEN}✅ Docker установлен${NC}"
}

# Установка Docker Compose
install_docker_compose() {
    echo -e "${YELLOW}🔧 Установка Docker Compose...${NC}"
    
    # Получение последней версии
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")')
    
    # Скачивание и установка
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    chmod +x /usr/local/bin/docker-compose
    
    # Создание симлинка
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    echo -e "${GREEN}✅ Docker Compose установлен${NC}"
}

# Настройка директорий
setup_directories() {
    echo -e "${YELLOW}📁 Настройка директорий...${NC}"
    
    # Создание структуры директорий
    mkdir -p "${PROJECT_DIR}"/{data,logs,backups,ssl}
    mkdir -p /var/log/"${PROJECT_NAME}"
    mkdir -p /opt/backups/"${PROJECT_NAME}"
    
    # Установка прав
    chown -R "${PROJECT_USER}":"${PROJECT_USER}" "${PROJECT_DIR}"
    chown -R "${PROJECT_USER}":"${PROJECT_USER}" /var/log/"${PROJECT_NAME}"
    chown -R "${PROJECT_USER}":"${PROJECT_USER}" /opt/backups/"${PROJECT_NAME}"
    
    chmod -R 755 "${PROJECT_DIR}"
    
    echo -e "${GREEN}✅ Директории настроены${NC}"
}

# Настройка мониторинга
setup_monitoring() {
    echo -e "${YELLOW}📊 Настройка базового мониторинга...${NC}"
    
    # Скрипт для мониторинга дискового пространства
    cat > /usr/local/bin/disk-monitor.sh << 'EOF'
#!/bin/bash
THRESHOLD=80
USAGE=$(df / | awk 'NR==2 {print $5}' | cut -d'%' -f1)

if [ $USAGE -gt $THRESHOLD ]; then
    echo "WARNING: Disk usage is ${USAGE}% on $(hostname)"
    # Здесь можно добавить отправку уведомлений
fi
EOF
    
    chmod +x /usr/local/bin/disk-monitor.sh
    
    # Добавление в cron (проверка каждый час)
    echo "0 * * * * root /usr/local/bin/disk-monitor.sh" >> /etc/crontab
    
    echo -e "${GREEN}✅ Базовый мониторинг настроен${NC}"
}

# Настройка автоматических обновлений безопасности
setup_auto_updates() {
    echo -e "${YELLOW}🔄 Настройка автоматических обновлений...${NC}"
    
    apt install -y unattended-upgrades
    
    # Конфигурация автоматических обновлений
    cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF
    
    # Включение автоматических обновлений
    echo 'APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";' > /etc/apt/apt.conf.d/20auto-upgrades
    
    echo -e "${GREEN}✅ Автоматические обновления настроены${NC}"
}

# Создание SSL сертификатов (самоподписанные для тестирования)
create_ssl_cert() {
    echo -e "${YELLOW}🔒 Создание самоподписанного SSL сертификата...${NC}"
    
    SSL_DIR="${PROJECT_DIR}/ssl"
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "${SSL_DIR}/key.pem" \
        -out "${SSL_DIR}/cert.pem" \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    
    chown "${PROJECT_USER}":"${PROJECT_USER}" "${SSL_DIR}"/*
    chmod 600 "${SSL_DIR}"/*
    
    echo -e "${GREEN}✅ SSL сертификат создан${NC}"
    echo -e "${YELLOW}⚠️ Это самоподписанный сертификат для тестирования${NC}"
    echo -e "${YELLOW}   В продакшене используйте Let's Encrypt${NC}"
}

# Информация об итогах
show_setup_summary() {
    echo ""
    echo -e "${GREEN}🎉 Настройка сервера завершена!${NC}"
    echo "==========================================="
    echo -e "${BLUE}📋 Что было настроено:${NC}"
    echo "  ✅ Система обновлена"
    echo "  ✅ Базовые пакеты установлены"
    echo "  ✅ Пользователь ${PROJECT_USER} создан"
    echo "  ✅ SSH безопасность настроена"
    echo "  ✅ Firewall настроен"
    echo "  ✅ Fail2Ban настроен"
    echo "  ✅ Docker установлен"
    echo "  ✅ Docker Compose установлен"
    echo "  ✅ Директории созданы"
    echo "  ✅ Базовый мониторинг настроен"
    echo "  ✅ Автоматические обновления настроены"
    echo "  ✅ SSL сертификат создан"
    echo ""
    echo -e "${BLUE}📁 Директории:${NC}"
    echo "  • Проект: ${PROJECT_DIR}"
    echo "  • Логи: /var/log/${PROJECT_NAME}"
    echo "  • Бэкапы: /opt/backups/${PROJECT_NAME}"
    echo ""
    echo -e "${YELLOW}⚠️ Следующие шаги:${NC}"
    echo "  1. Загрузите ваши файлы проекта в ${PROJECT_DIR}"
    echo "  2. Настройте .env файл"
    echo "  3. Запустите deploy.sh"
    echo "  4. Настройте доменное имя"
    echo "  5. Получите реальный SSL сертификат"
    echo ""
    echo -e "${BLUE}🔧 Полезные команды:${NC}"
    echo "  • Переключение на пользователя проекта: sudo -u ${PROJECT_USER} -i"
    echo "  • Проверка логов: journalctl -u ${PROJECT_NAME}"
    echo "  • Статус firewall: ufw status"
    echo "  • Статус fail2ban: fail2ban-client status"
}

# Основная функция
main() {
    echo -e "${YELLOW}🚀 Начинаем настройку сервера...${NC}"
    
    update_system
    install_basic_packages
    create_project_user
    setup_ssh_security
    setup_advanced_firewall
    setup_fail2ban
    install_docker
    install_docker_compose
    setup_directories
    setup_monitoring
    setup_auto_updates
    create_ssl_cert
    
    show_setup_summary
}

# Запуск
main 