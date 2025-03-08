add file:
echo "File for raspberry Olega2" > test-fileOleg2.txt
gsutil cp test-fileOleg2.txt gs://encoded-shape-452012-k8-secure-downloads/
gsutil cat gs://encoded-shape-452012-k8-secure-downloads/test-fileOleg2.txt

Чтобы предоставить права доступа к файлу в бакете Google Cloud Storage, вам нужно использовать команду gsutil acl. 
Вот как можно предоставить публичный доступ к файлу для чтения:
gsutil acl ch -u AllUsers:R gs://encoded-shape-452012-k8-secure-downloads/test-file4.txt


# Проверить, работает ли что-то на порту 5000
netstat -tuln | grep 5000
В одному терміналі треба запустити сервер:
# Если сервер не запущен, запустите его
python simple-download-server.py

В іншому терміналі:
Как использовать клиент:
# Получить список всех доступных файлов
python simple-download-client.py --server http://localhost:5000 --client user123 --list

# Проверить сколько скачиваний осталось
python simple-download-client.py --server http://localhost:5000 --client user123 --info

# Скачать конкретный файл (указав путь из списка файлов)
python simple-download-client.py --server http://localhost:5000 --client user123 --file zir_ai/aa7_pixhawk_219.json

# Скачать файл и сохранить его под другим именем
python simple-download-client.py --server http://localhost:5000 --client user123 --file zir_ai/aa7_pixhawk_219.json --output my-config.json

# Скачать файл в определенную директорию
python simple-download-client.py --server http://localhost:5000 --client user123 --file zir_ai/aa7_pixhawk_219.json --dir /path/to/downloads