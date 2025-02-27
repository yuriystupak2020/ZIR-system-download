#!/usr/bin/env python3
"""
Сервис автоматического обновления файлов для Raspberry Pi
"""

import os
import time
import json
import logging
import argparse
import schedule
from datetime import datetime
import signal
import sys

# Импортируем клиент для скачивания файлов
from raspberry_client import SecureDownloadClient

# Настройка логирования
log_dir = os.path.expanduser("~/logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
    
logging.basicConfig(
    filename=os.path.join(log_dir, "updater.log"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Добавляем вывод в консоль
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# Глобальные переменные
config_file = os.path.expanduser("~/updater_config.json")
running = True


def load_config():
    """Загружает конфигурацию из файла"""
    if not os.path.exists(config_file):
        # Создаем конфигурацию по умолчанию
        config = {
            "server_url": "https://your-server.com",
            "secret_key": "",
            "check_interval": 3600,  # Интервал проверки обновлений в секундах
            "download_dir": os.path.expanduser("~/downloads"),
            "auto_update": True,
            "last_check": None
        }
        
        # Сохраняем конфигурацию
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        logging.warning("Конфигурация не найдена, создана конфигурация по умолчанию")
        logging.warning(f"Пожалуйста, отредактируйте файл {config_file} и добавьте секретный ключ")
        
        return config
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logging.error(f"Ошибка при загрузке конфигурации: {str(e)}")
        return None


def save_config(config):
    """Сохраняет конфигурацию в файл"""
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Ошибка при сохранении конфигурации: {str(e)}")
        return False


def check_for_updates():
    """Проверяет наличие обновлений и скачивает их"""
    logging.info("Проверка обновлений...")
    
    # Загружаем конфигурацию
    config = load_config()
    if not config:
        logging.error("Не удалось загрузить конфигурацию")
        return
    
    # Проверяем, есть ли ключ
    if not config.get("secret_key"):
        logging.error("Секретный ключ не настроен")
        return
    
    # Создаем клиент
    client = SecureDownloadClient(
        server_url=config.get("server_url"),
        secret_key=config.get("secret_key"),
        download_dir=config.get("download_dir")
    )
    
    # Получаем список доступных файлов
    files = client.check_available_files()
    if not files:
        logging.warning("Нет доступных файлов или ошибка при получении списка")
        
        # Обновляем время последней проверки
        config["last_check"] = datetime.now().isoformat()
        save_config(config)
        return
    
    # Логируем количество доступных файлов
    logging.info(f"Доступно файлов: {len(files)}")
    
    # Проверяем, какие файлы нужно скачать
    download_queue = []
    
    for file_info in files:
        file_key = file_info.get("file_key")
        
        if not file_key:
            continue
            
        # Определяем путь для сохранения файла
        output_path = os.path.join(config.get("download_dir"), os.path.basename(file_key))
        
        # Проверяем, существует ли файл
        if not os.path.exists(output_path):
            # Файл не существует, добавляем в очередь
            download_queue.append({
                "file_key": file_key,
                "output_path": output_path,
                "reason": "new"
            })
            continue
            
        # Проверяем, требуется ли обновление (сравниваем дату обновления)
        if file_info.get("updated_at"):
            try:
                # Преобразуем строку в дату
                file_update_time = datetime.fromisoformat(file_info.get("updated_at"))
                
                # Получаем время модификации локального файла
                local_file_time = datetime.fromtimestamp(os.path.getmtime(output_path))
                
                # Если файл на сервере новее, добавляем в очередь
                if file_update_time > local_file_time:
                    download_queue.append({
                        "file_key": file_key,
                        "output_path": output_path,
                        "reason": "updated"
                    })
            except:
                # Если не удалось сравнить даты, пропускаем
                logging.warning(f"Не удалось сравнить даты обновления для {file_key}")
    
    # Скачиваем файлы из очереди
    for item in download_queue:
        file_key = item.get("file_key")
        output_path = item.get("output_path")
        reason = item.get("reason")
        
        logging.info(f"Скачивание файла {file_key} (причина: {reason})")
        
        # Скачиваем файл
        success = client.download_file(file_key, output_path)
        
        if success:
            logging.info(f"Файл {file_key} успешно скачан")
            
            # Проверяем, является ли файл исполняемым скриптом
            if file_key.endswith(".py") or file_key.endswith(".sh"):
                # Делаем файл исполняемым
                os.chmod(output_path, 0o755)
                logging.info(f"Файл {file_key} сделан исполняемым")
                
                # Если файл называется install.sh или setup.sh, запускаем его
                if os.path.basename(file_key) in ["install.sh", "setup.sh"] and config.get("auto_update", True):
                    logging.info(f"Запуск установочного скрипта {file_key}")
                    try:
                        os.system(f"bash {output_path}")
                        logging.info(f"Установочный скрипт {file_key} выполнен")
                    except Exception as e:
                        logging.error(f"Ошибка при запуске скрипта {file_key}: {str(e)}")
        else:
            logging.error(f"Ошибка при скачивании файла {file_key}")
    
    # Обновляем время последней проверки
    config["last_check"] = datetime.now().isoformat()
    save_config(config)
    
    logging.info(f"Проверка обновлений завершена, скачано файлов: {len(download_queue)}")


def signal_handler(sig, frame):
    """Обработчик сигналов для корректного завершения работы"""
    global running
    logging.info("Получен сигнал завершения, останавливаем сервис...")
    running = False
    sys.exit(0)


def main():
    """Основная функция"""
    # Настраиваем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Разбор аргументов командной строки
    parser = argparse.ArgumentParser(description='Сервис автоматического обновления файлов для Raspberry Pi')
    parser.add_argument('--config', help='Путь к файлу конфигурации')
    parser.add_argument('--check-now', action='store_true', help='Проверить обновления сейчас')
    parser.add_argument('--setup', action='store_true', help='Настроить секретный ключ')
    parser.add_argument('--interval', type=int, help='Интервал проверки обновлений в секундах')
    parser.add_argument('--server', help='URL сервера')
    
    args = parser.parse_args()
    
    # Если указан путь к конфигурации, используем его
    if args.config:
        global config_file
        config_file = args.config
    
    # Загружаем конфигурацию
    config = load_config()
    if not config:
        logging.error("Не удалось загрузить конфигурацию")
        return
    
    # Настраиваем ключ, если нужно
    if args.setup:
        key = input("Введите секретный ключ: ")
        config["secret_key"] = key
        save_config(config)
        logging.info("Секретный ключ сохранен")
    
    # Обновляем настройки, если указаны
    if args.interval:
        config["check_interval"] = args.interval
        save_config(config)
        logging.info(f"Интервал проверки обновлений установлен: {args.interval} секунд")
    
    if args.server:
        config["server_url"] = args.server
        save_config(config)
        logging.info(f"URL сервера установлен: {args.server}")
    
    # Проверяем обновления сейчас, если указано
    if args.check_now:
        check_for_updates()
        if not args.interval:  # Если не нужно запускать сервис
            return
    
    # Настраиваем расписание проверки обновлений
    interval_seconds = config.get("check_interval", 3600)
    schedule.every(interval_seconds).seconds.do(check_for_updates)
    
    logging.info(f"Сервис автоматического обновления запущен. Интервал: {interval_seconds} сек.")
    
    # Основной цикл
    while running:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()