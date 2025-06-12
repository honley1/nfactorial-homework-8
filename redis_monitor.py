#!/usr/bin/env python3
"""
Redis Monitor - скрипт для мониторинга состояния Redis
Использование: python redis_monitor.py
"""

import redis
import json
import time
from datetime import datetime
import sys

# Конфигурация подключения к Redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

class RedisMonitor:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB):
        try:
            self.redis_client = redis.Redis(
                host=host, 
                port=port, 
                db=db, 
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Тестируем подключение
            self.redis_client.ping()
            print(f"✅ Подключение к Redis ({host}:{port}) успешно!")
        except redis.ConnectionError:
            print(f"❌ Не удалось подключиться к Redis ({host}:{port})")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            sys.exit(1)

    def get_redis_info(self):
        """Получает основную информацию о Redis"""
        info = self.redis_client.info()
        return {
            'version': info['redis_version'],
            'mode': info['redis_mode'],
            'uptime': info['uptime_in_seconds'],
            'connected_clients': info['connected_clients'],
            'used_memory': info['used_memory_human'],
            'used_memory_peak': info['used_memory_peak_human'],
            'keyspace_hits': info['keyspace_hits'],
            'keyspace_misses': info['keyspace_misses'],
            'total_commands_processed': info['total_commands_processed'],
            'instantaneous_ops_per_sec': info['instantaneous_ops_per_sec']
        }

    def get_celery_queues(self):
        """Получает информацию о очередях Celery"""
        queues = {}
        try:
            # Основная очередь Celery
            main_queue_length = self.redis_client.llen('celery')
            queues['celery'] = main_queue_length
            
            # Дополнительные очереди
            for queue_name in ['email', 'reports', 'cleanup']:
                queue_length = self.redis_client.llen(queue_name)
                if queue_length > 0:
                    queues[queue_name] = queue_length
                    
        except Exception as e:
            print(f"❌ Ошибка получения очередей: {e}")
            
        return queues

    def get_celery_tasks(self):
        """Получает информацию о задачах Celery"""
        try:
            # Активные задачи
            active_tasks = []
            task_keys = self.redis_client.keys('celery-task-meta-*')
            
            for key in task_keys[:10]:  # Ограничиваем до 10 задач
                task_data = self.redis_client.get(key)
                if task_data:
                    try:
                        task_info = json.loads(task_data)
                        active_tasks.append({
                            'task_id': key.replace('celery-task-meta-', ''),
                            'status': task_info.get('status', 'UNKNOWN'),
                            'result': str(task_info.get('result', ''))[:100] + '...' if len(str(task_info.get('result', ''))) > 100 else task_info.get('result', '')
                        })
                    except json.JSONDecodeError:
                        continue
                        
            return active_tasks
        except Exception as e:
            print(f"❌ Ошибка получения задач: {e}")
            return []

    def get_database_keys(self):
        """Получает статистику по ключам в базе данных"""
        try:
            db_info = self.redis_client.info('keyspace')
            keys_info = {}
            
            for db, info in db_info.items():
                if db.startswith('db'):
                    keys_info[db] = {
                        'keys': info['keys'],
                        'expires': info['expires'],
                        'avg_ttl': info['avg_ttl']
                    }
                    
            return keys_info
        except Exception as e:
            print(f"❌ Ошибка получения ключей: {e}")
            return {}

    def monitor(self, interval=5, continuous=False):
        """Основная функция мониторинга"""
        try:
            while True:
                print("\n" + "="*60)
                print(f"🔄 Redis Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*60)
                
                # Основная информация
                print("\n📊 Основная информация:")
                info = self.get_redis_info()
                for key, value in info.items():
                    print(f"  {key}: {value}")
                
                # Очереди Celery
                print("\n📝 Очереди Celery:")
                queues = self.get_celery_queues()
                if queues:
                    for queue, length in queues.items():
                        print(f"  {queue}: {length} задач")
                else:
                    print("  Очереди пусты")
                
                # Активные задачи
                print("\n⚡ Активные задачи:")
                tasks = self.get_celery_tasks()
                if tasks:
                    for task in tasks[:5]:  # Показываем только первые 5
                        print(f"  ID: {task['task_id'][:8]}... | Статус: {task['status']} | Результат: {task['result']}")
                    if len(tasks) > 5:
                        print(f"  ... и еще {len(tasks) - 5} задач")
                else:
                    print("  Нет активных задач")
                
                # Ключи базы данных
                print("\n🗂️  Ключи базы данных:")
                db_keys = self.get_database_keys()
                if db_keys:
                    for db, info in db_keys.items():
                        print(f"  {db}: {info['keys']} ключей, {info['expires']} с истечением")
                else:
                    print("  Нет ключей в базе данных")
                
                if not continuous:
                    break
                    
                print(f"\n⏱️  Следующее обновление через {interval} секунд...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 Мониторинг остановлен")
        except Exception as e:
            print(f"\n❌ Ошибка мониторинга: {e}")

    def test_redis_operations(self):
        """Тестирует основные операции Redis"""
        print("\n🧪 Тестирование Redis операций:")
        
        try:
            # Тест SET/GET
            test_key = "test:monitor:ping"
            test_value = f"pong_{int(time.time())}"
            
            self.redis_client.set(test_key, test_value, ex=60)  # TTL 60 сек
            retrieved_value = self.redis_client.get(test_key)
            
            if retrieved_value == test_value:
                print("  ✅ SET/GET операции работают")
            else:
                print("  ❌ SET/GET операции не работают")
            
            # Тест списков (для очередей Celery)
            list_key = "test:monitor:list"
            self.redis_client.lpush(list_key, "test_item")
            list_length = self.redis_client.llen(list_key)
            self.redis_client.delete(list_key)
            
            if list_length > 0:
                print("  ✅ Операции со списками работают")
            else:
                print("  ❌ Операции со списками не работают")
            
            # Очистка тестовых данных
            self.redis_client.delete(test_key)
            
        except Exception as e:
            print(f"  ❌ Ошибка тестирования: {e}")


def main():
    print("🚀 Запуск Redis Monitor...")
    
    monitor = RedisMonitor()
    
    # Тестируем операции
    monitor.test_redis_operations()
    
    # Показываем текущее состояние
    monitor.monitor(continuous=False)
    
    # Спрашиваем пользователя о непрерывном мониторинге
    try:
        response = input("\n❓ Запустить непрерывный мониторинг? (y/N): ").strip().lower()
        if response in ['y', 'yes', 'д', 'да']:
            print("🔄 Запуск непрерывного мониторинга (Ctrl+C для остановки)...")
            monitor.monitor(interval=5, continuous=True)
    except KeyboardInterrupt:
        print("\n👋 До свидания!")


if __name__ == "__main__":
    main() 