import requests
import hmac
import hashlib
import time
import json


class SecureDownloadClient:
    def __init__(self, server_url, secret_key):
        self.server_url = server_url
        self.secret_key = secret_key
        self.device_id = self.get_raspberry_serial()

    def get_raspberry_serial(self):
        """Получение серийного номера Raspberry Pi"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('Serial'):
                        return line.split(':')[1].strip()
        except:
            raise Exception("Не удалось получить серийный номер Raspberry Pi")

    def generate_signature(self, timestamp):
        """Генерация подписи запроса"""
        message = f"{self.device_id}:{timestamp}"
        return hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

    def download_file(self, file_key):
        """Запрос и скачивание файла"""
        timestamp = str(int(time.time()))
        signature = self.generate_signature(timestamp)

        # Запрос URL для скачивания
        response = requests.post(
            f"{self.server_url}/request-download",
            json={
                'device_id': self.device_id,
                'timestamp': timestamp,
                'signature': signature,
                'file_key': file_key
            },
            headers={'User-Agent': f'RaspberryPi/{self.device_id}'}
        )

        if response.status_code == 200:
            download_url = response.json()['download_url']

            # Скачивание файла
            file_response = requests.get(download_url)
            if file_response.status_code == 200:
                with open(file_key, 'wb') as f:
                    f.write(file_response.content)
                return True

        error = response.json().get('error', 'Unknown error')
        print(f"Ошибка: {error}")
        return False


# Пример использования
if __name__ == "__main__":
    client = SecureDownloadClient(
        server_url='https://your-server.com',
        secret_key='your-secret-key'  # Этот ключ должен быть уникальным для каждого устройства
    )

    success = client.download_file('example-file.zip')
    if success:
        print("Файл успешно скачан")
    else:
        print("Ошибка при скачивании файла")