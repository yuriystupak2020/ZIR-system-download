import requests
import os
import json
import argparse
import time
from urllib.parse import urlparse, unquote

class SimpleDownloadClient:
    def __init__(self, server_url, client_id, download_dir=None):
        """
        Простой клиент для загрузки файлов с сервера или внешних URL
        
        Args:
            server_url (str): URL сервера скачивания
            client_id (str): ID клиента для отслеживания скачиваний
            download_dir (str, optional): Директория для сохранения загруженных файлов
        """
        self.server_url = server_url.rstrip('/')
        self.client_id = client_id
        self.download_dir = download_dir or os.path.join(os.getcwd(), "downloads")
        
        # Создаем директорию для скачивания, если она не существует
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            
        print(f"Клиент инициализирован:")
        print(f"  - Сервер: {self.server_url}")
        print(f"  - ID клиента: {self.client_id}")
        print(f"  - Директория скачивания: {self.download_dir}")
    
    def get_available_files(self):
        """
        Получает список доступных файлов с сервера
        
        Returns:
            dict: Информация о файлах и лимитах скачивания
        """
        try:
            url = f"{self.server_url}/list-files?client_id={self.client_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Ошибка при получении списка файлов: {response.status_code}")
                print(f"Ответ сервера: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при получении списка файлов: {str(e)}")
            return None
    
    def download_file(self, file_path, output_filename=None):
        """
        Скачивает файл с сервера или внешнего URL
        
        Args:
            file_path (str): Путь к файлу на сервере (category/filename.json)
            output_filename (str, optional): Имя файла для сохранения
            
        Returns:
            bool: Результат скачивания
        """
        try:
            # Сначала получаем URL для скачивания
            url = f"{self.server_url}/get-download-url?client_id={self.client_id}&file_path={file_path}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"Ошибка при получении URL для скачивания: {response.status_code}")
                print(f"Ответ сервера: {response.text}")
                return False
            
            # Получаем данные для скачивания
            data = response.json()
            download_url = data.get("download_url")
            external_url = data.get("external_url")
            
            # Определяем имя файла для сохранения
            if not output_filename:
                output_filename = os.path.basename(file_path)
                if output_filename.endswith('.json') and external_url:
                    # Для внешних файлов - берем только имя без расширения .json
                    output_filename = os.path.splitext(output_filename)[0]
            
            output_path = os.path.join(self.download_dir, output_filename)
            
            # Если у нас есть внешний URL, скачиваем напрямую с него
            if external_url:
                print(f"Скачивание файла с внешнего URL: {external_url}")
                print(f"Сохранение в: {output_path}")
                
                # Создаем директорию, если нужно
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                
                # Скачиваем файл с внешнего URL
                download_response = requests.get(external_url, stream=True, timeout=30)
                
                if download_response.status_code != 200:
                    print(f"Ошибка при скачивании с внешнего URL: {download_response.status_code}")
                    return False
                
                # Сохраняем файл
                with open(output_path, 'wb') as f:
                    for chunk in download_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                print(f"Файл успешно скачан: {output_path}")
                print(f"Использовано {data.get('downloads_count', '?')} из {data.get('max_downloads', '?')} скачиваний")
                
                return True
            
            # Если у нас есть локальный URL, скачиваем с сервера
            elif download_url:
                print(f"Скачивание файла: {file_path}")
                print(f"URL скачивания: {self.server_url}{download_url}")
                print(f"Сохранение в: {output_path}")
                
                # Создаем директорию, если нужно
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                
                # Скачиваем файл с сервера
                download_response = requests.get(f"{self.server_url}{download_url}", stream=True, timeout=30)
                
                if download_response.status_code != 200:
                    print(f"Ошибка при скачивании файла: {download_response.status_code}")
                    print(f"Ответ сервера: {download_response.text}")
                    return False
                
                # Сохраняем файл
                with open(output_path, 'wb') as f:
                    for chunk in download_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                print(f"Файл успешно скачан: {output_path}")
                print(f"Использовано {data.get('downloads_count', '?')} из {data.get('max_downloads', '?')} скачиваний")
                
                return True
            
            else:
                print("Не получен URL для скачивания или внешний URL")
                return False
            
        except Exception as e:
            print(f"Ошибка при скачивании файла: {str(e)}")
            return False
    
    def add_external_url(self, external_url, category=None, file_name=None, product_name=None, file_size=None):
        """
        Добавляет внешний URL в базу файлов
        
        Args:
            external_url (str): Внешний URL файла
            category (str, optional): Категория файла
            file_name (str, optional): Имя файла
            product_name (str, optional): Название продукта
            file_size (int, optional): Размер файла
            
        Returns:
            bool: Результат добавления
        """
        try:
            # Если категория не указана, используем "external"
            if not category:
                category = "external"
            
            # Если имя файла не указано, генерируем его
            if not file_name:
                file_name = f"file_{int(time.time())}"
            
            # Если имя продукта не указано, используем имя файла
            if not product_name:
                product_name = file_name
            
            # Отправляем запрос на добавление внешнего URL
            response = requests.post(
                f"{self.server_url}/add-external-url",
                json={
                    "client_id": self.client_id,
                    "external_url": external_url,
                    "category": category,
                    "file_name": file_name,
                    "product_name": product_name,
                    "file_size": file_size or 0
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Внешний URL успешно добавлен: {data.get('file_path')}")
                return True
            else:
                print(f"Ошибка при добавлении внешнего URL: {response.status_code}")
                print(f"Ответ сервера: {response.text}")
                return False
                
        except Exception as e:
            print(f"Ошибка при добавлении внешнего URL: {str(e)}")
            return False
    
    def show_downloads_info(self):
        """Выводит информацию о лимитах скачивания"""
        try:
            # Получаем информацию с сервера
            files_info = self.get_available_files()
            
            if not files_info:
                print("Не удалось получить информацию о скачиваниях")
                return
            
            downloads_count = files_info.get("downloads_count", 0)
            max_downloads = files_info.get("max_downloads", 0)
            remaining = files_info.get("remaining_downloads", 0)
            
            print(f"\nИнформация о скачиваниях для клиента {self.client_id}:")
            print(f"  - Всего скачиваний: {downloads_count}")
            print(f"  - Максимально разрешено: {max_downloads}")
            print(f"  - Осталось: {remaining}")
            
            if remaining <= 0:
                print("\nВНИМАНИЕ: Лимит скачиваний исчерпан!")
            elif remaining < 3:
                print(f"\nВНИМАНИЕ: Осталось всего {remaining} скачиваний!")
        
        except Exception as e:
            print(f"Ошибка при получении информации о скачиваниях: {str(e)}")
    
    def download_all_files(self, filter_category=None):
        """
        Скачивает все доступные файлы с сервера
        
        Args:
            filter_category (str, optional): Категория для фильтрации файлов
            
        Returns:
            tuple: (скачано, всего, ошибок)
        """
        # Получаем список доступных файлов
        files_info = self.get_available_files()
        if not files_info:
            print("Не удалось получить список файлов")
            return 0, 0, 0
        
        files = files_info.get("files", [])
        remaining = files_info.get("remaining_downloads", 0)
        
        # Фильтруем файлы по категории, если указана
        if filter_category:
            files = [f for f in files if filter_category in f.get("file_path", "")]
        
        if not files:
            print("Нет доступных файлов для скачивания")
            return 0, 0, 0
        
        print(f"\nНачинаем скачивание всех доступных файлов ({len(files)} файлов, осталось {remaining} скачиваний):")
        
        # Проверяем, достаточно ли осталось скачиваний
        if remaining < len(files):
            print(f"ВНИМАНИЕ: Доступно только {remaining} скачиваний из {len(files)} файлов.")
            print("Некоторые файлы не будут скачаны из-за лимита скачиваний.")
        
        # Скачиваем каждый файл
        downloaded = 0
        errors = 0
        
        for i, file in enumerate(files, 1):
            file_path = file.get("file_path", "")
            product_name = file.get("product_name", "")
            
            # Проверяем лимит скачиваний перед продолжением
            current_info = self.get_available_files()
            if current_info and current_info.get("remaining_downloads", 0) <= 0:
                print("\nЛимит скачиваний исчерпан. Прекращаем загрузку.")
                break
            
            print(f"\n[{i}/{len(files)}] Скачивание {product_name} ({file_path})...")
            
            # Определяем имя файла для сохранения (сохраняем структуру директорий)
            output_name = os.path.basename(file_path)
            if output_name.endswith('.json'):
                # Убираем расширение .json для файлов с внешним URL
                has_external = file.get("external_url", None) is not None
                if has_external:
                    output_name = os.path.splitext(output_name)[0]
                    
            output_path = file_path
            if output_path.endswith('.json') and file.get("external_url", None) is not None:
                output_path = os.path.splitext(output_path)[0]
            
            # Скачиваем файл
            result = self.download_file(file_path, output_path)
            
            if result:
                downloaded += 1
            else:
                errors += 1
                print(f"Ошибка при скачивании файла {file_path}")
            
            # Небольшая пауза между запросами, чтобы не перегружать сервер
            time.sleep(0.5)
        
        print(f"\nЗавершено скачивание файлов.")
        print(f"Успешно скачано: {downloaded}/{len(files)}")
        if errors > 0:
            print(f"Ошибок: {errors}")
        
        return downloaded, len(files), errors

def main():
    parser = argparse.ArgumentParser(description='Клиент для загрузки файлов с сервера')
    parser.add_argument('--server', default='http://localhost:5000', help='URL сервера')
    parser.add_argument('--client', required=True, help='ID клиента')
    parser.add_argument('--dir', help='Директория для сохранения файлов')
    parser.add_argument('--list', action='store_true', help='Получить список доступных файлов')
    parser.add_argument('--info', action='store_true', help='Показать информацию о лимитах скачивания')
    parser.add_argument('--file', help='Путь к файлу для скачивания (category/filename.json)')
    parser.add_argument('--output', help='Имя файла для сохранения')
    parser.add_argument('--add-url', help='Добавить внешний URL в базу файлов')
    parser.add_argument('--category', help='Категория для внешнего URL')
    parser.add_argument('--name', help='Имя файла для внешнего URL')
    parser.add_argument('--product-name', help='Название продукта для внешнего URL')
    parser.add_argument('--all', action='store_true', help='Скачать все доступные файлы')
    
    args = parser.parse_args()
    
    # Создаем клиент
    client = SimpleDownloadClient(
        server_url=args.server,
        client_id=args.client,
        download_dir=args.dir
    )
    
    # Показываем информацию о лимитах скачивания
    if args.info:
        client.show_downloads_info()
    
    # Выводим список доступных файлов
    if args.list:
        files_info = client.get_available_files()
        if files_info:
            files = files_info.get("files", [])
            remaining = files_info.get("remaining_downloads", 0)
            
            print(f"\nДоступные файлы (осталось {remaining} скачиваний):\n")
            
            # Группируем файлы по категории
            files_by_category = {}
            for file in files:
                category = file.get("category")
                if category not in files_by_category:
                    files_by_category[category] = []
                files_by_category[category].append(file)
            
            # Выводим файлы по категориям
            for category, category_files in files_by_category.items():
                print(f"\n[{category}]")
                for file in category_files:
                    file_path = file.get("file_path", "")
                    product_name = file.get("product_name", file.get("file_name", ""))
                    file_size = file.get("size", 0)
                    external_url = file.get("external_url", None)
                    
                    # Форматируем размер файла
                    if file_size < 1024:
                        size_str = f"{file_size} байт"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} КБ"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} МБ"
                    
                    url_info = " (внешний URL)" if external_url else ""
                    print(f"  - {file_path} - {product_name} ({size_str}){url_info}")
        else:
            print("Не удалось получить список файлов")
    
    # Добавляем внешний URL в базу файлов
    if args.add_url:
        client.add_external_url(
            external_url=args.add_url,
            category=args.category,
            file_name=args.name,
            product_name=args.product_name
        )
    
    # Скачиваем все доступные файлы
    if args.all:
        # Если указана директория, она может быть фильтром категории
        category_filter = None
        if args.dir and not os.path.isabs(args.dir) and not args.dir.startswith('./') and not args.dir.startswith('../'):
            category_filter = args.dir
        
        client.download_all_files(category_filter)
    # Скачиваем указанный файл
    elif args.file:
        success = client.download_file(args.file, args.output)
        if success:
            print("\nФайл успешно скачан!")
        else:
            print("\nОшибка при скачивании файла")
    
    # Если не указаны параметры, выводим справку
    if not (args.list or args.info or args.file or args.add_url or args.all):
        parser.print_help()

if __name__ == '__main__':
    main()