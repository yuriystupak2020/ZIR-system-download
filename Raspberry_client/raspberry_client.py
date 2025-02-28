import requests
import hmac
import hashlib
import time
import json
import os
import logging
from datetime import datetime

class SecureDownloadClient:
    def __init__(self, server_url, secret_key, download_dir=None, retries=3, retry_delay=5):
        """
        Инициализация клиента для безопасного скачивания файлов
        
        Args:
            server_url (str): URL сервера скачивания
            secret_key (str): Секретный ключ для подписи запросов
            download_dir (str, optional): Директория для скачивания файлов
            retries (int, optional): Количество повторных попыток при ошибке
            retry_delay (int, optional): Задержка между повторными попытками в секундах
        """
        self.server_url = server_url
        self.secret_key = secret_key
        self.device_id = self.get_raspberry_serial()
        self.download_dir = download_dir or os.path.join(os.path.expanduser("~"), "downloads")
        self.retries = retries
        self.retry_delay = retry_delay
        
        # Создаем директорию для скачивания если она не существует
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            
        # Настройка логирования
        self.setup_logging()
        
    def setup_logging(self):
        """Настройка логирования"""
        log_file = os.path.join(self.download_dir, "download_log.txt")
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Добавляем вывод в консоль
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        self.logger.addHandler(console)

    def get_raspberry_serial(self):
        """Получение серийного номера Raspberry Pi"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('Serial'):
                        return line.split(':')[1].strip()
            
            # Если не нашли серийный номер, пробуем другие способы
            try:
                import subprocess
                # Пытаемся получить MAC-адрес как альтернативный идентификатор
                mac = subprocess.check_output("cat /sys/class/net/eth0/address", shell=True).decode('utf-8').strip()
                return f"mac-{mac.replace(':', '')}"
            except:
                pass
                
            # Генерируем уникальный ID и сохраняем его
            id_file = os.path.join(os.path.expanduser("~"), ".device_id")
            if os.path.exists(id_file):
                with open(id_file, 'r') as f:
                    return f.read().strip()
            else:
                import uuid
                device_id = f"rpi-{str(uuid.uuid4())}"
                with open(id_file, 'w') as f:
                    f.write(device_id)
                return device_id
                
        except Exception as e:
            self.logger.error(f"Не удалось получить серийный номер: {str(e)}")
            raise Exception("Не удалось получить ID устройства Raspberry Pi")

    def generate_signature(self, timestamp):
        """Генерация подписи запроса"""
        message = f"{self.device_id}:{timestamp}"
        return hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

    def download_file(self, file_key, output_path=None):
        """
        Запрос и скачивание файла
        
        Args:
            file_key (str): Ключ файла для скачивания
            output_path (str, optional): Полный путь для сохранения файла
            
        Returns:
            bool: Результат скачивания
        """
        timestamp = str(int(time.time()))
        signature = self.generate_signature(timestamp)
        
        # Определяем путь для сохранения файла
        if output_path is None:
            output_path = os.path.join(self.download_dir, os.path.basename(file_key))
            
        self.logger.info(f"Запрос на скачивание файла: {file_key}")
        self.logger.info(f"ID устройства: {self.device_id}")

        # Запрос URL для скачивания с повторными попытками
        for attempt in range(self.retries):
            try:
                response = requests.post(
                    f"{self.server_url}/request-download",
                    json={
                        'device_id': self.device_id,
                        'timestamp': timestamp,
                        'signature': signature,
                        'file_key': file_key
                    },
                    headers={'User-Agent': f'RaspberryPi/{self.device_id}'},
                    timeout=30  # Устанавливаем таймаут
                )
                
                # Проверяем ответ сервера
                if response.status_code == 200:
                    download_url = response.json().get('download_url')
                    
                    if not download_url:
                        self.logger.error("URL для скачивания отсутствует в ответе сервера")
                        return False
                        
                    self.logger.info(f"Получен URL для скачивания, начинаем скачивание")
                    
                    # Скачивание файла с поддержкой больших файлов
                    # return self._download_large_file(download_url, output_path)
                    return self._download_large_file(download_url, output_path, file_key)
                    
                elif response.status_code == 403:
                    error = response.json().get('error', 'Unknown error')
                    self.logger.error(f"Доступ запрещен: {error}")
                    # Если доступ запрещен, нет смысла повторять
                    return False
                else:
                    error = response.json().get('error', f"HTTP error: {response.status_code}")
                    self.logger.warning(f"Попытка {attempt+1}/{self.retries}: {error}")
                    
                    if attempt < self.retries - 1:
                        time.sleep(self.retry_delay)
                    
            except Exception as e:
                self.logger.warning(f"Попытка {attempt+1}/{self.retries}: Ошибка соединения: {str(e)}")
                if attempt < self.retries - 1:
                    time.sleep(self.retry_delay)
        
        self.logger.error("Превышено максимальное количество попыток скачивания")
        return False
        
    # def _download_large_file(self, url, output_path, chunk_size=8192):
    def _download_large_file(self, url, output_path, file_key=None, chunk_size=8192):
        """
        Скачивание файла чанками для поддержки больших файлов
        
        Args:
            url (str): URL для скачивания
            output_path (str): Путь для сохранения файла
            chunk_size (int, optional): Размер чанка при скачивании
            
        Returns:
            bool: Результат скачивания
        """
        try:
            # Создаем временный файл для скачивания
            temp_file = f"{output_path}.download"
            
            # Отправляем запрос на скачивание файла
            with requests.get(url, stream=True, timeout=60) as response:
                if response.status_code != 200:
                    self.logger.error(f"Ошибка при скачивании: HTTP {response.status_code}")
                    return False
                
                # Получаем размер файла, если доступен
                file_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                
                # Открываем файл для записи
                with open(temp_file, 'wb') as f:
                    start_time = time.time()
                    last_log_time = start_time
                    
                    # Скачиваем файл чанками
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Выводим прогресс каждые 5 секунд
                            current_time = time.time()
                            if current_time - last_log_time > 5:
                                if file_size > 0:
                                    percent = (downloaded / file_size) * 100
                                    self.logger.info(f"Прогресс скачивания: {percent:.1f}% ({downloaded}/{file_size} байт)")
                                else:
                                    self.logger.info(f"Скачано: {downloaded} байт")
                                last_log_time = current_time
            
            # Проверяем успешность скачивания
            if os.path.exists(temp_file):
                # Переименовываем временный файл в целевой
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(temp_file, output_path)
                
                download_time = time.time() - start_time
                file_size = os.path.getsize(output_path)
                
                self.logger.info(f"Файл успешно скачан: {output_path}")
                self.logger.info(f"Размер: {file_size} байт, Время: {download_time:.1f} сек.")
                
                # Записываем информацию о скачивании в лог-файл
                self._log_download_info(file_key, output_path, file_size)
                
                return True
            else:
                self.logger.error("Временный файл не создан")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка при скачивании файла: {str(e)}")
            
            # Удаляем временный файл в случае ошибки
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if file_key:
                self._log_download_info(file_key, output_path, file_size)
                
            return False
            
    def _log_download_info(self, file_key, output_path, file_size):
        """Записывает информацию о скачивании в локальный файл"""
        log_file = os.path.join(self.download_dir, "downloads.json")
        
        # Читаем существующий лог, если он есть
        downloads = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    downloads = json.load(f)
            except:
                pass
                
        # Добавляем новую запись
        downloads.append({
            'device_id': self.device_id,
            'file_key': file_key,
            'output_path': output_path,
            'file_size': file_size,
            'timestamp': datetime.now().isoformat()
        })
        
        # Сохраняем лог
        with open(log_file, 'w') as f:
            json.dump(downloads, f, indent=2)
            
    def check_available_files(self):
        """
        Возвращает список доступных файлов для скачивания
        
        Returns:
            list: Предопределенный список файлов
        """
        # Используем предопределенный список файлов из бакета
        files = [
            {
                'file_key': 'test-file.txt',  # Имя файла, которое мы нашли в бакете
                'name': 'Test File',          # Отображаемое имя (может быть любым)
                'size': 0,                    # Размер файла (не обязательно указывать точно)
                'updated_at': datetime.now().isoformat()  # Время последнего обновления
            },
            {
                'file_key': 'test-file2.txt',  # Имя файла, которое мы нашли в бакете
                'name': 'test-file2.txt',          # Отображаемое имя (может быть любым)
                'size': 0,                    # Размер файла (не обязательно указывать точно)
                'updated_at': datetime.now().isoformat()  # Время последнего обновления
            }
        ]
        
        self.logger.info(f"Используем предопределенный список файлов: {len(files)} файлов")
        return files
        # """
        # Запрашивает список доступных файлов с сервера
        
        # Returns:
        #     list: Список доступных файлов или None в случае ошибки
        # """
        # timestamp = str(int(time.time()))
        # signature = self.generate_signature(timestamp)
        
        # self.logger.info(f"Запрос списка файлов. Device ID: {self.device_id}")
        # self.logger.info(f"Timestamp: {timestamp}")
        # self.logger.info(f"Signature: {signature}")
        
        # try:
        #     # url = f"{self.server_url}/list-files"
        #     url = f"{self.server_url}/request-download"
        #     self.logger.info(f"URL запроса: {url}")
            
        #     payload = {
        #         'device_id': self.device_id,
        #         'timestamp': timestamp,
        #         'signature': signature
        #     }
            
        #     self.logger.info(f"Отправляемые данные: {json.dumps(payload)}")
            
        #     response = requests.post(
        #         url,
        #         json=payload,
        #         headers={'User-Agent': f'RaspberryPi/{self.device_id}'},
        #         timeout=30
        #     )
            
        #     self.logger.info(f"Код ответа: {response.status_code}")
        #     self.logger.info(f"Тело ответа: {response.text}")
            
        #     # Безопасный парсинг JSON
        #     if response.text.strip():
        #         try:
        #             data = response.json()
                    
        #             if response.status_code == 200:
        #                 files = data.get('files', [])
        #                 self.logger.info(f"Получен список доступных файлов: {len(files)} файлов")
        #                 return files
        #             else:
        #                 error = data.get('error', f"HTTP error: {response.status_code}")
        #                 self.logger.error(f"Ошибка при получении списка файлов: {error}")
        #         except json.JSONDecodeError as e:
        #             self.logger.error(f"Не удалось распарсить JSON ответа: {str(e)}")
        #     else:
        #         self.logger.error("Получен пустой ответ от сервера")
                
        #     return None
                
        # except Exception as e:
        #     self.logger.error(f"Ошибка при запросе списка файлов: {str(e)}")
        #     import traceback
        #     self.logger.error(f"Трассировка: {traceback.format_exc()}")
        #     return None

# Пример использования
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Клиент для безопасного скачивания файлов')
    parser.add_argument('--server', default='https://your-server.com', help='URL сервера скачивания')
    parser.add_argument('--key', required=True, help='Секретный ключ для подписи запросов')
    parser.add_argument('--file', help='Ключ файла для скачивания')
    parser.add_argument('--output', help='Путь для сохранения файла')
    parser.add_argument('--list', action='store_true', help='Получить список доступных файлов')
    parser.add_argument('--dir', help='Директория для скачивания файлов')
    
    args = parser.parse_args()
    
    # Создаем клиент
    client = SecureDownloadClient(
        server_url=args.server,
        secret_key=args.key,
        download_dir=args.dir
    )
    
    if args.list:
        # Получаем список доступных файлов
        files = client.check_available_files()
        if files:
            print("Доступные файлы:")
            for file in files:
                print(f" - {file}")
        else:
            print("Не удалось получить список файлов")
    
    elif args.file:
        # Скачиваем указанный файл
        success = client.download_file(args.file, args.output)
        if success:
            print("Файл успешно скачан")
        else:
            print("Ошибка при скачивании файла")
    else:
        print("Укажите файл для скачивания (--file) или запросите список файлов (--list)")