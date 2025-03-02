import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random
import uuid
import string
from faker import Faker

# Initialize Firebase
def initialize_firebase():
    """Initialize Firebase with your credentials"""
    # Replace with path to your Firebase service account key
    cred = credentials.Certificate("../config/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    return firestore.client()

def generate_serial_number():
    """Generate a random Raspberry Pi serial number"""
    # Format: 8 characters alphanumeric
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_client_data(num_clients=10):
    """Generate random client data"""
    fake = Faker()
    clients = []
    
    for _ in range(num_clients):
        # Generate between 1-5 Raspberry Pi serial numbers for this client
        num_devices = random.randint(1, 5)
        raspberry_serials = [generate_serial_number() for _ in range(num_devices)]
        
        # Generate between 1-10 licenses
        num_licenses = random.randint(1, 10)
        
        client = {
            "client_id": str(uuid.uuid4()),
            "name": fake.company(),
            "contact_person": fake.name(),
            "email": fake.company_email(),
            "phone": fake.phone_number(),
            "address": fake.address(),
            "registration_date": fake.date_time_this_year().isoformat(),
            "licenses": {
                "count": num_licenses,
                "type": random.choice(["Basic", "Standard", "Premium", "Enterprise"]),
                "expiration_date": fake.date_time_between(start_date="+30d", end_date="+365d").isoformat()
            },
            "raspberry_serials": raspberry_serials,
            "active": random.choice([True, False]),
            "notes": fake.text(max_nb_chars=200) if random.random() > 0.7 else ""
        }
        clients.append(client)
    
    return clients

def upload_to_firebase(db, clients):
    """Upload generated client data to Firebase Firestore"""
    clients_collection = db.collection('clients')
    
    for client in clients:
        clients_collection.document(client["client_id"]).set(client)
    
    print(f"Successfully uploaded {len(clients)} clients to Firebase Firestore.")

def main():
    """Main function to generate and upload client data"""
    # Number of clients to generate
    num_clients = 10
    
    # Generate client data
    print(f"Generating {num_clients} client records...")
    clients = generate_client_data(num_clients)
    
    # Initialize Firebase and upload data
    print("Initializing Firebase connection...")
    db = initialize_firebase()
    
    print("Uploading client data to Firebase...")
    upload_to_firebase(db, clients)
    
    print("Client data generation complete!")

if __name__ == "__main__":
    main()
