from google.cloud import storage

class CloudStorage:
    def __init__(self):
        self.storage_client = storage.Client()  # Создаём клиента

    def upload_file(self, bucket_name, source_file, destination_blob):
        """Загружает файл в указанный бакет GCS."""
        bucket = self.storage_client.bucket(bucket_name)  # Получаем бакет
        blob = bucket.blob(destination_blob)  # Создаём объект (blob)
        blob.upload_from_filename(source_file)  # Загружаем файл
        print(f"Файл {source_file} загружен в {bucket_name}/{destination_blob}")

# Использование:
cloud = CloudStorage()
cloud.upload_file("my-bucket", "/home/user/ZIR/local_file.txt", "remote_file.txt")
