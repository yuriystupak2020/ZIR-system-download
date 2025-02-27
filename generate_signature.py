import hmac
import hashlib

device_id = "test-device-001"
timestamp = "1645000000"
secret_key = "fhX7tG9yZN2w8kL5vQ3pP6mD1rJ4sA0uB9cE2xF3"  # Ваш реальный ключ из app.yaml

message = f"{device_id}:{timestamp}"
signature = hmac.new(
    secret_key.encode(),
    message.encode(),
    hashlib.sha256
).hexdigest()

print(f"Подпись: {signature}")
