import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Initialize Firebase
def initialize_firebase():
    """Initialize Firebase with your credentials"""
    # Replace with path to your Firebase service account key
    cred = credentials.Certificate("../config/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    return firestore.client()

def generate_products_structure():
    """
    Generate structured product categories with configuration files
    using the new naming format: a|b|p + a|d + size + _fc + _camera + .json
    """
    # Define the three main product categories and their subcategories
    products_structure = {
        "zir_ai": {
            "name": "Zir AI",
            "description": "AI-powered drone systems for autonomous operations",
            "config_files": [
                "aa7_pixhawk_219.json",     # analog 7" Pixhawk with IMX219
                "aa10_ardupilot_477.json",   # analog 10" ArduPilot with IMX477
                "aa15_naza_219.json",        # analog 15" Naza with IMX219
                "ad5_dji_477.json",          # digital 5" DJI with IMX477
                "ad7_betaflight_219.json",   # digital 7" Betaflight with IMX219
                "ad10_kiss_477.json",        # digital 10" KISS with IMX477
                "aa5_pixhawk_219.json",      # analog 5" Pixhawk with IMX219
                "ad15_ardupilot_477.json",   # digital 15" ArduPilot with IMX477
                "aa7_betaflight_477.json",   # analog 7" Betaflight with IMX477
                "ad10_naza_219.json"         # digital 10" Naza with IMX219
            ]
        },
        "zir_bace": {
            "name": "Zir Bace",
            "description": "Base drone systems for copters with advanced capabilities",
            "config_files": [
                "ba7_pixhawk_219.json",      # analog 7" Pixhawk with IMX219
                "ba10_ardupilot_477.json",   # analog 10" ArduPilot with IMX477
                "ba15_naza_219.json",        # analog 15" Naza with IMX219
                "bd5_dji_477.json",          # digital 5" DJI with IMX477
                "bd7_betaflight_219.json",   # digital 7" Betaflight with IMX219
                "bd10_kiss_477.json",        # digital 10" KISS with IMX477
                "ba5_pixhawk_219.json",      # analog 5" Pixhawk with IMX219
                "bd15_ardupilot_477.json",   # digital 15" ArduPilot with IMX477
                "ba7_betaflight_477.json",   # analog 7" Betaflight with IMX477
                "bd10_naza_219.json"         # digital 10" Naza with IMX219
            ]
        },
        "zir_plane": {
            "name": "Zir Plane",
            "description": "Advanced fixed-wing aircraft systems",
            "config_files": [
                "pa7_pixhawk_219.json",      # analog 7" Pixhawk with IMX219
                "pa10_ardupilot_477.json",   # analog 10" ArduPilot with IMX477
                "pa15_naza_219.json",        # analog 15" Naza with IMX219
                "pd5_dji_477.json",          # digital 5" DJI with IMX477
                "pd7_betaflight_219.json",   # digital 7" Betaflight with IMX219
                "pd10_kiss_477.json",        # digital 10" KISS with IMX477
                "pa5_pixhawk_219.json",      # analog 5" Pixhawk with IMX219
                "pd15_ardupilot_477.json",   # digital 15" ArduPilot with IMX477
                "pa7_betaflight_477.json",   # analog 7" Betaflight with IMX477
                "pd10_naza_219.json"         # digital 10" Naza with IMX219
            ]
        }
    }
    
    return products_structure

def generate_config_content(config_name):
    """Generate sample content for each configuration file based on its name"""
    # Parse filename to extract information
    # Format is: a|b|p + a|d + size + _fc + _camera + .json
    
    # Extract product line (first letter)
    product_line_code = config_name[0]
    product_line = {
        'a': 'Zir AI',
        'b': 'Zir Bace',
        'p': 'Zir Plane'
    }.get(product_line_code, 'Unknown')
    
    # Extract connection type (second letter)
    connection_type_code = config_name[1]
    connection_type = {
        'a': 'Analog',
        'd': 'Digital'
    }.get(connection_type_code, 'Unknown')
    
    # Extract size before the first underscore
    size_end = config_name.find('_')
    size = config_name[2:size_end] + " inch"
    
    # Extract flight controller
    fc_start = size_end + 1
    fc_end = config_name.find('_', fc_start)
    fc = config_name[fc_start:fc_end].capitalize()
    
    # Extract camera
    camera_start = fc_end + 1
    camera_end = config_name.find('.', camera_start)
    camera_code = config_name[camera_start:camera_end]
    camera = {
        '219': 'Sony IMX219',
        '477': 'Sony IMX477'
    }.get(camera_code, 'Unknown')
    
    # Create configuration content
    config_content = {
        "name": f"{product_line} {connection_type} {size} {fc}",
        "product_line": product_line,
        "connection_type": connection_type,
        "size": size,
        "flight_controller": fc,
        "camera": camera,
        "settings": {
            "pid": {
                "p_gain": 1.5,
                "i_gain": 0.5,
                "d_gain": 0.2
            },
            "rates": {
                "roll_rate": 720,
                "pitch_rate": 720,
                "yaw_rate": 650
            },
            "filters": {
                "gyro_lpf": "90Hz",
                "dterm_lpf": "100Hz"
            }
        },
        "firmware": {
            "version": "1.0.0",
            "release_date": "2024-03-01"
        }
    }
    
    return config_content

def upload_to_firebase(db, products_structure):
    """Upload product categories and config files to Firebase Firestore"""
    products_collection = db.collection('products_config_files')
    
    # Upload each main category with its config files
    for category_id, category_data in products_structure.items():
        # Create the main document
        products_collection.document(category_id).set({
            "name": category_data["name"],
            "description": category_data["description"]
        })
        
        # Create a config_files subcollection for each product
        config_collection = products_collection.document(category_id).collection('config_files')
        
        # Add each config file to the subcollection
        for config_file in category_data["config_files"]:
            # Generate content for this config file
            config_content = generate_config_content(config_file)
            
            # Use the filename (without extension) as the document ID
            doc_id = config_file.split('.')[0]
            config_collection.document(doc_id).set(config_content)
    
    print(f"Successfully uploaded product categories and configuration files to Firebase Firestore.")

def create_json_files(products_structure):
    """Create physical JSON files from configuration data"""
    import json
    import os
    
    # Create directory for config files if it doesn't exist
    config_dir = "config_files"
    os.makedirs(config_dir, exist_ok=True)
    
    for category_id, category_data in products_structure.items():
        # Create category subfolder
        category_dir = os.path.join(config_dir, category_id)
        os.makedirs(category_dir, exist_ok=True)
        
        # Create each config file
        for config_filename in category_data["config_files"]:
            # Generate content for this config file
            config_content = generate_config_content(config_filename)
            
            # Create the full path for the file
            file_path = os.path.join(category_dir, config_filename)
            
            # Write the JSON data to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_content, f, indent=4)
    
    print(f"Successfully created JSON configuration files in '{config_dir}' directory.")
    return config_dir

def main():
    """Main function to generate and upload product structure"""
    # Generate product structure with the new config files
    print("Creating product category structure...")
    products_structure = generate_products_structure()
    
    # Initialize Firebase and upload data
    print("Initializing Firebase connection...")
    db = initialize_firebase()
    
    print("Uploading product structure to Firebase...")
    upload_to_firebase(db, products_structure)
    
    # Create physical JSON files
    print("Creating configuration JSON files...")
    config_files_dir = create_json_files(products_structure)
    
    print(f"Product structure upload complete!")
    print(f"Configuration files created in the '{config_files_dir}' directory.")

if __name__ == "__main__":
    main()