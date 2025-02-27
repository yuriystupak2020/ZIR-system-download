import hmac
import hashlib
import time
import requests
from functools import wraps
from flask import request, abort, current_app
import logging
import os
from google.cloud import secretmanager
from config import CONFIG
from datetime import datetime
import maxminddb

# Настройка логирования для Cloud Logging
from google.cloud import logging as cloud_logging
from google.cloud.logging.handlers import CloudLoggingHandler


class SecurityManager:
    def __init__(self, app):
        self.app = app
        self.failed_attempts = {}
        self.suspicious_ips = set()
        self.setup_logging()
        
        # Загружаем GeoIP базу
        self.geodb_path = 'GeoLite2-Country.mmdb'
        # В production нужно загрузить файл GeoIP базы в контейнер

    def setup_logging(self):
        """Настройка логирования для Google Cloud"""
        # Для App Engine логи автоматически идут в Cloud Logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # В production можно настроить структурированное логирование
        # client = cloud_logging.Client()
        # handler = CloudLoggingHandler(client)
        # cloud_logger = logging.getLogger('cloudLogger')
        # cloud_logger.setLevel(logging.INFO)
        # cloud_logger.addHandler(handler)

    def verify_signature(self, device_id, timestamp, signature):
        """Проверка подписи запроса"""
        secret_key = self.app.config['SECRET_KEY']
        message = f"{device_id}:{timestamp}"
        expected_signature = hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)

    def check_rate_limit(self, device_id):
        """Проверка частоты запросов"""
        current_time = time.time()
        if device_id in self.failed_attempts:
            attempts = [t for t in self.failed_attempts[device_id]
                        if current_time - t < 3600]
            self.failed_attempts[device_id] = attempts
            if len(attempts) >= CONFIG['MAX_ATTEMPTS']:
                return False
        return True

    def record_failed_attempt(self, device_id):
        """Запись неудачной попытки"""
        if device_id not in self.failed_attempts:
            self.failed_attempts[device_id] = []
        self.failed_attempts[device_id].append(time.time())

    def check_location(self, ip_address):
        """Проверка геолокации IP"""
        # В production нужно использовать более надежный метод
        # определения страны, например, Cloud Functions + MaxMind
        try:
            # Проверяем, есть ли файл GeoIP базы
            if os.path.exists(self.geodb_path):
                with maxminddb.open_database(self.geodb_path) as reader:
                    response = reader.get(ip_address)
                    if response and 'country' in response and 'iso_code' in response['country']:
                        return response['country']['iso_code'] in CONFIG['ALLOWED_COUNTRIES']
            
            # Если файла нет или ошибка - логируем и пропускаем
            logging.warning(f"GeoIP check failed for {ip_address}, allowing access")
            return True  # В production сделать более строгую проверку
        except Exception as e:
            logging.error(f"Error checking location: {str(e)}")
            return True  # В production сделать более строгую проверку

    def send_alert(self, message, level='warning'):
        """Отправка уведомлений о подозрительной активности"""
        # В GCP лучше использовать Cloud Pub/Sub или Cloud Functions
        # для отправки уведомлений вместо SMTP
        logging.warning(f"SECURITY ALERT: {message}")
        
        # В production можно использовать Cloud Functions для отправки SMS или email
        # или настроить Cloud Monitoring для алертов