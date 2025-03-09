from flask import Flask, request, jsonify, send_from_directory
import os
import json
import hashlib
import time
from datetime import datetime

app = Flask(__name__)

# Путь к существующим конфигурационным файлам и директория для счетчиков скачиваний
CONFIG_DIR = "Firebase_client/config_files2"
DOWNLOADS_DIR = "downloads_data"

# Максимальное количество скачиваний для одного клиента
MAX_DOWNLOADS = 100

def ensure_directories():
    """Создание необходимых директорий, если они отсутствуют"""
    # Проверяем существование директории с конфигурационными файлами
    if not os.path.exists(CONFIG_DIR):
        raise Exception(f"Директория с конфигурационными файлами не найдена: {CONFIG_DIR}")
    
    # Создаем директорию для хранения данных о скачиваниях
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)

def get_client_downloads(client_id):
    """Получает количество скачиваний для клиента"""
    downloads_file = os.path.join(DOWNLOADS_DIR, f"{client_id}.json")
    
    if os.path.exists(downloads_file):
        try:
            with open(downloads_file, 'r') as f:
                downloads_data = json.load(f)
                return downloads_data.get("downloads", 0), downloads_data.get("files", [])
        except Exception as e:
            print(f"Ошибка при чтении файла скачиваний: {str(e)}")
            return 0, []
    else:
        return 0, []

def update_client_downloads(client_id, file_path):
    """Обновляет счетчик скачиваний для клиента"""
    downloads_file = os.path.join(DOWNLOADS_DIR, f"{client_id}.json")
    downloads_count, downloaded_files = get_client_downloads(client_id)
    
    # Увеличиваем счетчик скачиваний
    downloads_count += 1
    
    # Добавляем файл в список скачанных, если его там еще нет
    if file_path not in downloaded_files:
        downloaded_files.append(file_path)
    
    # Обновляем данные
    downloads_data = {
        "downloads": downloads_count,
        "files": downloaded_files,
        "last_download": datetime.now().isoformat()
    }
    
    # Записываем данные в файл
    with open(downloads_file, 'w') as f:
        json.dump(downloads_data, f, indent=4)
    
    return downloads_count

def check_download_limit(client_id):
    """Проверяет, не превышен ли лимит скачиваний для клиента"""
    downloads_count, _ = get_client_downloads(client_id)
    return downloads_count < MAX_DOWNLOADS

@app.route('/')
def home():
    """Домашняя страница"""
    return jsonify({
        "status": "online",
        "service": "Simple Download Server",
        "version": "1.0.0"
    })

@app.route('/list-files', methods=['GET'])
def list_files():
    """Возвращает список доступных файлов из существующей директории"""
    client_id = request.args.get('client_id')
    
    if not client_id:
        return jsonify({"error": "Client ID is required"}), 400
    
    # Сканируем директорию с файлами
    all_files = []
    
    if os.path.exists(CONFIG_DIR):
        categories = [d for d in os.listdir(CONFIG_DIR) if os.path.isdir(os.path.join(CONFIG_DIR, d))]
        
        for category_id in categories:
            category_path = os.path.join(CONFIG_DIR, category_id)
            
            # Определяем название категории
            category_name = {
                "zir_ai": "Zir AI",
                "zir_bace": "Zir Bace",
                "zir_plane": "Zir Plane"
            }.get(category_id, category_id)
            
            # Сканируем файлы в категории
            json_files = [f for f in os.listdir(category_path) if f.endswith('.json')]
            
            for file_name in json_files:
                file_path = f"{category_id}/{file_name}"
                
                # Получаем размер файла
                full_path = os.path.join(CONFIG_DIR, file_path)
                file_size = os.path.getsize(full_path)
                
                # Пытаемся получить дополнительную информацию из файла
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        file_data = json.load(f)
                        product_name = file_data.get("name", file_name)
                except:
                    product_name = file_name
                
                all_files.append({
                    "file_path": file_path,
                    "file_name": file_name,
                    "product_name": product_name,
                    "category": category_name,
                    "size": file_size
                })
    
    # Получаем текущий счетчик скачиваний
    downloads_count, _ = get_client_downloads(client_id)
    
    return jsonify({
        "files": all_files,
        "downloads_count": downloads_count,
        "max_downloads": MAX_DOWNLOADS,
        "remaining_downloads": MAX_DOWNLOADS - downloads_count
    })

@app.route('/download/<path:file_path>')
def download_file(file_path):
    """Обработчик для скачивания файла"""
    client_id = request.args.get('client_id')
    
    if not client_id:
        return jsonify({"error": "Client ID is required"}), 400
    
    # Проверяем лимит скачиваний
    if not check_download_limit(client_id):
        return jsonify({
            "error": "Download limit exceeded",
            "downloads_count": get_client_downloads(client_id)[0],
            "max_downloads": MAX_DOWNLOADS
        }), 403
    
    # Убеждаемся, что запрашиваемый файл находится в CONFIG_DIR и является безопасным
    full_path = os.path.abspath(os.path.join(CONFIG_DIR, file_path))
    if not full_path.startswith(os.path.abspath(CONFIG_DIR)):
        return jsonify({"error": "Invalid file path"}), 403
    
    if not os.path.exists(full_path):
        return jsonify({"error": "File not found"}), 404
    
    # Обновляем счетчик скачиваний
    downloads_count = update_client_downloads(client_id, file_path)
    
    # Разделяем путь на директорию и имя файла
    directory, filename = os.path.split(full_path)
    
    # Регистрируем скачивание в консоли
    print(f"Client {client_id} downloaded {file_path} ({downloads_count}/{MAX_DOWNLOADS})")
    
    # Возвращаем файл
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/get-download-url', methods=['GET'])
def get_download_url():
    """Генерирует URL для скачивания файла"""
    client_id = request.args.get('client_id')
    file_path = request.args.get('file_path')
    
    if not client_id or not file_path:
        return jsonify({"error": "Client ID and file path are required"}), 400
    
    # Проверяем лимит скачиваний
    if not check_download_limit(client_id):
        return jsonify({
            "error": "Download limit exceeded",
            "downloads_count": get_client_downloads(client_id)[0],
            "max_downloads": MAX_DOWNLOADS
        }), 403
    
    # Проверяем существование файла
    full_path = os.path.abspath(os.path.join(CONFIG_DIR, file_path))
    if not full_path.startswith(os.path.abspath(CONFIG_DIR)):
        return jsonify({"error": "Invalid file path"}), 403
    
    if not os.path.exists(full_path):
        return jsonify({"error": "File not found"}), 404
    
    # Генерируем временный токен для скачивания
    timestamp = int(time.time())
    token = hashlib.md5(f"{client_id}:{file_path}:{timestamp}".encode()).hexdigest()
    
    # Формируем URL для скачивания
    download_url = f"/download/{file_path}?client_id={client_id}&token={token}&t={timestamp}"
    
    return jsonify({
        "download_url": download_url,
        "expires_in": 3600,  # URL действителен в течение 1 часа
        "downloads_count": get_client_downloads(client_id)[0],
        "max_downloads": MAX_DOWNLOADS
    })

if __name__ == '__main__':
    ensure_directories()
    
    # Выводим список найденных категорий и файлов
    print(f"Найдены следующие файлы в директории {CONFIG_DIR}:")
    if os.path.exists(CONFIG_DIR):
        categories = [d for d in os.listdir(CONFIG_DIR) if os.path.isdir(os.path.join(CONFIG_DIR, d))]
        for category in categories:
            category_path = os.path.join(CONFIG_DIR, category)
            files = [f for f in os.listdir(category_path) if f.endswith('.json')]
            print(f"  - {category} ({len(files)} файлов)")
    
    print(f"\nСервер запущен. Максимальное количество скачиваний на клиента: {MAX_DOWNLOADS}")
    app.run(host='0.0.0.0', port=5000, debug=True)