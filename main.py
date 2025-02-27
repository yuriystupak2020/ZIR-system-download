from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from security import SecurityManager
from config import CONFIG
import os
from google.cloud import storage
from datetime import datetime, timedelta
import logging
import json
from google.cloud import firestore

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
security = SecurityManager(app)

# Настройка rate limiting
limiter = Limiter(
    app=app,  # Обновленный синтаксис для новых версий
    key_func=get_remote_address,
    default_limits=[CONFIG['RATE_LIMIT']]
)


class SecureDownloadManager:
    def __init__(self, bucket_name):
        # Используем GCS вместо S3
        self.storage_client = storage.Client()
        self.bucket_name = bucket_name
        self.db = firestore.Client()
        
    def generate_download_url(self, device_id, file_key):
        """Генерирует URL для скачивания файла из GCS"""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(file_key)
            
            # Проверим, существует ли файл
            if not blob.exists():
                logging.error(f"File {file_key} not found in bucket {self.bucket_name}")
                return None
            
            # Создаем URL с временным токеном доступа
            url = f"https://storage.googleapis.com/{self.bucket_name}/{file_key}"
            
            # Логируем скачивание в Firestore
            self.log_download(device_id, file_key)
            
            return url
        except Exception as e:
            logging.error(f"Error generating download URL: {str(e)}")
            return None
            
    def log_download(self, device_id, file_key):
        """Записывает информацию о скачивании в Firestore"""
        downloads_ref = self.db.collection('device_downloads')
        
        # Проверяем существующие записи
        query = downloads_ref.where('device_id', '==', device_id).where('file_key', '==', file_key).limit(1)
        docs = list(query.stream())
        
        if docs:
            # Обновляем существующую запись
            doc_ref = docs[0].reference
            doc_data = docs[0].to_dict()
            doc_ref.update({
                'download_count': doc_data.get('download_count', 0) + 1,
                'last_download': datetime.now(),
                'ip_address': request.remote_addr,
                'user_agent': request.user_agent.string
            })
        else:
            # Создаем новую запись
            downloads_ref.add({
                'device_id': device_id,
                'file_key': file_key,
                'download_count': 1,
                'last_download': datetime.now(),
                'ip_address': request.remote_addr,
                'user_agent': request.user_agent.string
            })
            
    def log_security_event(self, event_type, device_id, ip_address, details):
        """Записывает информацию о событиях безопасности в Firestore"""
        self.db.collection('security_events').add({
            'timestamp': datetime.now(),
            'event_type': event_type,
            'device_id': device_id,
            'ip_address': ip_address,
            'details': details
        })


@app.route('/request-download', methods=['POST'])
@limiter.limit(CONFIG['RATE_LIMIT'])
def request_download():
    data = request.json
    device_id = data.get('device_id')
    timestamp = data.get('timestamp')
    signature = data.get('signature')
    file_key = data.get('file_key')
    ip_address = request.remote_addr

    # Проверка обязательных параметров
    if not all([device_id, timestamp, signature, file_key]):
        return jsonify({'error': 'Missing required parameters'}), 400

    # Проверка геолокации
    if not security.check_location(ip_address):
        security.send_alert(
            f"Suspicious access from {ip_address} for device {device_id}"
        )
        return jsonify({'error': 'Access denied by location'}), 403

    # Проверка подписи
    if not security.verify_signature(device_id, timestamp, signature):
        security.record_failed_attempt(device_id)
        security.send_alert(
            f"Invalid signature from device {device_id} at {ip_address}"
        )
        return jsonify({'error': 'Invalid signature'}), 403

    # Проверка rate limit
    if not security.check_rate_limit(device_id):
        security.send_alert(
            f"Rate limit exceeded for device {device_id} at {ip_address}"
        )
        return jsonify({'error': 'Too many attempts'}), 429

    # Генерация URL и логирование
    bucket_name = os.environ.get('GCS_BUCKET_NAME', 'your-bucket-name')
    manager = SecureDownloadManager(bucket_name)
    download_url = manager.generate_download_url(device_id, file_key)

    if download_url:
        manager.log_security_event(
            'successful_download',
            device_id,
            ip_address,
            file_key
        )
        return jsonify({'download_url': download_url})
    else:
        return jsonify({'error': 'Failed to generate URL'}), 500


@app.route('/', methods=['GET'])
def home():
    """Простая домашняя страница для проверки работы приложения"""
    return jsonify({
        'status': 'online',
        'service': 'Secure Download API',
        'version': '1.0.0'
    })


if __name__ == '__main__':
    # Используется только при локальном запуске
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)

# from flask import Flask, request, jsonify
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
# from security import SecurityManager
# from config import CONFIG
# import os
# from google.cloud import storage
# from datetime import datetime, timedelta
# import logging
# import json
# from google.cloud import firestore

# app = Flask(__name__)
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
# security = SecurityManager(app)

# # Настройка rate limiting
# limiter = Limiter(
#     app=app,  # Обновленный синтаксис для новых версий
#     key_func=get_remote_address,
#     default_limits=[CONFIG['RATE_LIMIT']]
# )


# class SecureDownloadManager:
#     def __init__(self, bucket_name):
#         # Используем GCS вместо S3
#         self.storage_client = storage.Client()
#         self.bucket_name = bucket_name
#         self.db = firestore.Client()
        
#     def generate_download_url(self, device_id, file_key):
#         """Генерирует URL для скачивания файла из GCS"""
#         try:
#             bucket = self.storage_client.bucket(self.bucket_name)
#             blob = bucket.blob(file_key)
            
#             # Проверим, существует ли файл
#             if not blob.exists():
#                 logging.error(f"File {file_key} not found in bucket {self.bucket_name}")
#                 return None
            
#             # Создаем публичный URL для скачивания, доступный с любого устройства
#             # Используем подписанный URL с ограниченным временем действия для безопасности
#             url = blob.generate_signed_url(
#                 expiration=datetime.now() + timedelta(minutes=30),
#                 method="GET"
#             )
            
#             # Логируем скачивание в Firestore
#             self.log_download(device_id, file_key)
            
#             return url
#         except Exception as e:
#             logging.error(f"Error generating download URL: {str(e)}")
#             return None
            
#     def log_download(self, device_id, file_key):
#         """Записывает информацию о скачивании в Firestore"""
#         downloads_ref = self.db.collection('device_downloads')
        
#         # Проверяем существующие записи
#         query = downloads_ref.where('device_id', '==', device_id).where('file_key', '==', file_key).limit(1)
#         docs = list(query.stream())
        
#         if docs:
#             # Обновляем существующую запись
#             doc_ref = docs[0].reference
#             doc_data = docs[0].to_dict()
#             doc_ref.update({
#                 'download_count': doc_data.get('download_count', 0) + 1,
#                 'last_download': datetime.now(),
#                 'ip_address': request.remote_addr,
#                 'user_agent': request.user_agent.string
#             })
#         else:
#             # Создаем новую запись
#             downloads_ref.add({
#                 'device_id': device_id,
#                 'file_key': file_key,
#                 'download_count': 1,
#                 'last_download': datetime.now(),
#                 'ip_address': request.remote_addr,
#                 'user_agent': request.user_agent.string
#             })
            
#     def log_security_event(self, event_type, device_id, ip_address, details):
#         """Записывает информацию о событиях безопасности в Firestore"""
#         self.db.collection('security_events').add({
#             'timestamp': datetime.now(),
#             'event_type': event_type,
#             'device_id': device_id,
#             'ip_address': ip_address,
#             'details': details
#         })


# @app.route('/request-download', methods=['POST'])
# @limiter.limit(CONFIG['RATE_LIMIT'])
# def request_download():
#     data = request.json
#     device_id = data.get('device_id')
#     timestamp = data.get('timestamp')
#     signature = data.get('signature')
#     file_key = data.get('file_key')
#     ip_address = request.remote_addr

#     # Проверка обязательных параметров
#     if not all([device_id, timestamp, signature, file_key]):
#         return jsonify({'error': 'Missing required parameters'}), 400

#     # Логируем IP-адрес вместо блокировки по геолокации
#     logging.info(f"Download requested from IP: {ip_address} for device {device_id}")

#     # Проверка подписи
#     if not security.verify_signature(device_id, timestamp, signature):
#         security.record_failed_attempt(device_id)
#         security.send_alert(
#             f"Invalid signature from device {device_id} at {ip_address}"
#         )
#         return jsonify({'error': 'Invalid signature'}), 403

#     # Проверка rate limit
#     if not security.check_rate_limit(device_id):
#         security.send_alert(
#             f"Rate limit exceeded for device {device_id} at {ip_address}"
#         )
#         return jsonify({'error': 'Too many attempts'}), 429

#     # Генерация URL и логирование
#     bucket_name = os.environ.get('GCS_BUCKET_NAME', 'your-bucket-name')
#     manager = SecureDownloadManager(bucket_name)
#     download_url = manager.generate_download_url(device_id, file_key)

#     if download_url:
#         manager.log_security_event(
#             'successful_download',
#             device_id,
#             ip_address,
#             file_key
#         )
#         return jsonify({'download_url': download_url})
#     else:
#         return jsonify({'error': 'Failed to generate URL'}), 500


# @app.route('/', methods=['GET'])
# def home():
#     """Простая домашняя страница для проверки работы приложения"""
#     return jsonify({
#         'status': 'online',
#         'service': 'Secure Download API',
#         'version': '1.0.0'
#     })


# if __name__ == '__main__':
#     # Используется только при локальном запуске
#     app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)