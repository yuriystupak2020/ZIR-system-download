from google.cloud import firestore

class CloudDatabase:
    def __init__(self):
        self.db = firestore.Client()  # Инициализация клиента Firestore

    def add_document(self, collection_name, document_id, data):
        """Добавить документ в коллекцию Firestore"""
        collection_ref = self.db.collection(collection_name)  # Получаем ссылку на коллекцию
        document_ref = collection_ref.document(document_id)  # Получаем ссылку на документ
        document_ref.set(data)  # Записываем данные в документ
        print(f"Документ {document_id} добавлен в коллекцию {collection_name}")

# Пример использования
cloud_db = CloudDatabase()
cloud_db.add_document("users", "user1", {"name": "Alice", "age": 30})
