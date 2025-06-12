#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔴 Redis Management Commands${NC}"
echo "================================"

# Функция для выполнения Redis команд
redis_cmd() {
    echo -e "${YELLOW}Выполняется: $1${NC}"
    docker exec -it task-manager-redis redis-cli $1
    echo ""
}

case $1 in
    "status")
        echo -e "${GREEN}📊 Статус Redis${NC}"
        redis_cmd "INFO server"
        ;;
    "memory")
        echo -e "${GREEN}💾 Использование памяти${NC}"
        redis_cmd "INFO memory"
        ;;
    "queues")
        echo -e "${GREEN}📝 Очереди Celery${NC}"
        echo "Основная очередь:"
        redis_cmd "LLEN celery"
        echo "Очередь email:"
        redis_cmd "LLEN email"
        echo "Очередь reports:"
        redis_cmd "LLEN reports"
        echo "Очередь cleanup:"
        redis_cmd "LLEN cleanup"
        ;;
    "tasks")
        echo -e "${GREEN}⚡ Задачи Celery${NC}"
        redis_cmd "KEYS celery-task-meta-*"
        ;;
    "clear-tasks")
        echo -e "${RED}🗑️ Очистка всех задач${NC}"
        read -p "Вы уверены? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            redis_cmd "DEL celery-task-meta-*"
            echo -e "${GREEN}✅ Задачи очищены${NC}"
        fi
        ;;
    "clear-queues")
        echo -e "${RED}🗑️ Очистка всех очередей${NC}"
        read -p "Вы уверены? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            redis_cmd "DEL celery email reports cleanup"
            echo -e "${GREEN}✅ Очереди очищены${NC}"
        fi
        ;;
    "monitor")
        echo -e "${GREEN}🔄 Мониторинг Redis (Ctrl+C для выхода)${NC}"
        docker exec -it task-manager-redis redis-cli MONITOR
        ;;
    "cli")
        echo -e "${GREEN}🖥️ Redis CLI${NC}"
        docker exec -it task-manager-redis redis-cli
        ;;
    "ping")
        echo -e "${GREEN}🏓 Ping Redis${NC}"
        redis_cmd "PING"
        ;;
    *)
        echo -e "${YELLOW}Доступные команды:${NC}"
        echo "  status       - Статус сервера"
        echo "  memory       - Использование памяти"
        echo "  queues       - Статус очередей Celery"
        echo "  tasks        - Активные задачи"
        echo "  clear-tasks  - Очистить все задачи"
        echo "  clear-queues - Очистить все очереди"
        echo "  monitor      - Мониторинг команд"
        echo "  cli          - Интерактивный CLI"
        echo "  ping         - Проверка подключения"
        echo ""
        echo -e "${YELLOW}Использование:${NC}"
        echo "  ./redis_commands.sh <команда>"
        echo ""
        echo -e "${YELLOW}Примеры:${NC}"
        echo "  ./redis_commands.sh status"
        echo "  ./redis_commands.sh queues"
        echo "  ./redis_commands.sh monitor"
        ;;
esac 