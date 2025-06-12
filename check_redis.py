#!/usr/bin/env python3
"""
Быстрая проверка Redis подключения и основных операций
"""

import redis
import sys

def check_redis():
    try:
        # Подключение к Redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # Проверка подключения
        response = r.ping()
        if response:
            print("✅ Redis доступен!")
        
        # Получение базовой информации
        info = r.info()
        print(f"📊 Версия Redis: {info['redis_version']}")
        print(f"📊 Время работы: {info['uptime_in_seconds']} секунд")
        print(f"📊 Подключенных клиентов: {info['connected_clients']}")
        print(f"📊 Используемая память: {info['used_memory_human']}")
        
        # Проверка очередей Celery
        celery_queue = r.llen('celery')
        print(f"📝 Очередь Celery: {celery_queue} задач")
        
        # Проверка ключей задач
        task_keys = r.keys('celery-task-meta-*')
        print(f"⚡ Активных задач: {len(task_keys)}")
        
        return True
        
    except redis.ConnectionError:
        print("❌ Не удалось подключиться к Redis")
        print("💡 Убедитесь, что Redis запущен:")
        print("   - Docker: docker-compose up redis")
        print("   - Локально: redis-server")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Проверка Redis...")
    success = check_redis()
    sys.exit(0 if success else 1)