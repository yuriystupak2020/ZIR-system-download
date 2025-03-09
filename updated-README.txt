
# Запустите сервер с помощью команды:
python updated-server.py



# Получить список всех доступных файлов
python updated-client.py --server http://localhost:5000 --client user123 --list

# Проверить сколько скачиваний осталось
python updated-client.py --server http://localhost:5000 --client user123 --info

# Скачать конкретный файл (указав путь из списка файлов)
python updated-client.py --server http://localhost:5000 --client user123 --file zir_ai/aa7_pixhawk_219.json

# Скачать все файлы
python updated-client.py --server http://localhost:5000 --client user123 --all

# Скачать все файлы из определенной категории
python updated-client.py --server http://localhost:5000 --client user123 --all --dir zir_ai/

# Скачать файл и сохранить его под другим именем
python updated-client.py --server http://localhost:5000 --client user123 --file zir_ai/aa7_pixhawk_219.json --output my-config.json

# Скачать файл в определенную директорию
python updated-client.py --server http://localhost:5000 --client user123 --file zir_ai/aa7_pixhawk_219.json --dir /path/to/downloads



# Добавить внешний URL в базу файлов
python updated-client.py --server http://localhost:5000 --client user123 --add-url https://example.com/file.zip --category documents --name example-file