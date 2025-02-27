# Установка зависимостей
pip install -r requirements.txt

# Запуск клиента
python raspberry_client.py


На Raspberry Pi устанавливается только:
raspberry_client.py    # Клиентский код
requirements.txt       # Зависимости для клиента:
- requests
- cryptography



Сделайте файл авто-обновления исполняемым:
chmod +x auto_updater.py


Установите необходимые зависимости:
pip3 install requests schedule



mkdir -p ~/downloads
mkdir -p ~/logs

Когда вы захотите использовать ваш клиент или скрипт автообновления, всегда сначала активируйте виртуальное окружение:
cd ~/auto-loader
source venv/bin/activate

Для запуска клиента для скачивания отдельного файла:
python raspberry_client.py --server https://your-server.com --key your-secret-key --file example-file.zip

Для запуска скрипта автообновления:
./auto_updater.py --setup
# Введите секретный ключ когда будет запрошено

# Проверка обновлений вручную
./auto_updater.py --check-now

Для выхода из виртуального окружения, когда закончите работу:
deactivate

Если вы хотите настроить автозапуск сервиса обновления при включении Raspberry Pi, вам понадобится создать systemd сервис:
# Создайте файл сервиса
sudo nano /etc/systemd/system/cloud-updater.service

Содержимое файла сервиса:
[Unit]
Description=Cloud File Updater Service
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/auto-loader
ExecStart=/home/pi/auto-loader/venv/bin/python /home/pi/auto-loader/auto_updater.py
Restart=always
RestartSec=10
StandardOutput=append:/home/pi/logs/service.log
StandardError=append:/home/pi/logs/service-error.log

[Install]
WantedBy=multi-user.target


Настройка и запуск сервиса:
# Перезагрузите systemd для обнаружения нового сервиса
sudo systemctl daemon-reload

# Включите сервис для автозапуска при загрузке
sudo systemctl enable cloud-updater.service

# Запустите сервис
sudo systemctl start cloud-updater.service

# Проверьте статус сервиса
sudo systemctl status cloud-updater.service
