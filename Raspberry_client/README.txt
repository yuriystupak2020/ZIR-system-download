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

https://encoded-shape-452012-k8.lm.r.appspot.com     fhX7tG9yZN2w8kL5vQ3pP6mD1rJ4sA0uB9cE2xF3

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

------------------------------------------------------------
./auto_updater.py --check-now

#айди росбери узнать
(venv) pi@raspberrypi:~/auto-loader $ python3 -c "import os; print(''.join([line.split(':')[1].strip() for line in open('/proc/cpuinfo') if line.startswith('Serial')]))"
f270e2abbeb3e872

