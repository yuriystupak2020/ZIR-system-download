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
    Generate structured product categories and subcategories
    No random generation - just fixed structure
    """
    # Define the three main product categories and their subcategories
    products_structure = {
        "zir_ai": {
            "name": "Zir AI",
            "description": "AI-powered drone systems for autonomous operations",
            "subcategories": {
                "flight_controllers": {
                    "pixhawk": {
                        "name": "Pixhawk",
                        "variants": ["Pixhawk 4", "Pixhawk 6X", "Pixhawk Mini"],
                        "config_files": ["zir_ai_pixhawk_standard.cfg", "zir_ai_pixhawk_advanced.cfg"]
                    },
                    "ardupilot": {
                        "name": "ArduPilot",
                        "variants": ["ArduCopter", "ArduPlane", "ArduRover"],
                        "config_files": ["zir_ai_ardupilot_basic.cfg", "zir_ai_ardupilot_pro.cfg"]
                    },
                    "naza": {
                        "name": "Naza-M",
                        "variants": ["Naza-M Lite", "Naza-M V2"],
                        "config_files": ["zir_ai_naza_standard.cfg"]
                    },
                    "dji_a3": {
                        "name": "DJI A3",
                        "variants": ["A3", "A3 Pro"],
                        "config_files": ["zir_ai_dji_a3_basic.cfg", "zir_ai_dji_a3_advanced.cfg"]
                    },
                    "betaflight": {
                        "name": "Betaflight F4",
                        "variants": ["F4", "F7", "F405"],
                        "config_files": ["zir_ai_betaflight_race.cfg", "zir_ai_betaflight_cinema.cfg"]
                    },
                    "kiss": {
                        "name": "KISS FC",
                        "variants": ["KISS FC v1", "KISS FC v2", "KISS Ultra"],
                        "config_files": ["zir_ai_kiss_standard.cfg"]
                    }
                },
                "sizes": {
                    "micro": {
                        "name": "Micro",
                        "description": "Under 100mm frame size",
                        "weight_range": "50g-100g",
                        "typical_motors": "1102-1105"
                    },
                    "mini": {
                        "name": "Mini",
                        "description": "100-200mm frame size",
                        "weight_range": "100g-250g",
                        "typical_motors": "1306-2204"
                    },
                    "medium": {
                        "name": "Medium",
                        "description": "200-350mm frame size",
                        "weight_range": "250g-500g",
                        "typical_motors": "2205-2306"
                    },
                    "standard": {
                        "name": "Standard",
                        "description": "350-500mm frame size",
                        "weight_range": "500g-1000g",
                        "typical_motors": "2306-2807"
                    },
                    "large": {
                        "name": "Large",
                        "description": "500-650mm frame size",
                        "weight_range": "1000g-2000g",
                        "typical_motors": "3508-4108"
                    },
                    "xlarge": {
                        "name": "X-Large",
                        "description": "Over 650mm frame size",
                        "weight_range": "2000g+",
                        "typical_motors": "4114-6215"
                    }
                },
                "cameras": {
                    "sony_imx219": {
                        "name": "Sony IMX219",
                        "resolution": "3280×2464",
                        "sensor_size": "1/4 inch"
                    },
                    "sony_imx477": {
                        "name": "Sony IMX477",
                        "resolution": "4056×3040",
                        "sensor_size": "1/2.3 inch"
                    },
                    "gopro_hero9": {
                        "name": "GoPro Hero 9",
                        "resolution": "5120×2880",
                        "sensor_size": "1/2.3 inch"
                    },
                    "runcam_eagle": {
                        "name": "RunCam Eagle",
                        "resolution": "800TVL",
                        "sensor_size": "1/3 inch"
                    },
                    "foxeer_predator": {
                        "name": "Foxeer Predator",
                        "resolution": "1000TVL",
                        "sensor_size": "1/3 inch"
                    },
                    "dji_fpv": {
                        "name": "DJI FPV Camera",
                        "resolution": "1080p",
                        "sensor_size": "1/2.3 inch"
                    },
                    "caddx_vista": {
                        "name": "Caddx Vista",
                        "resolution": "720p",
                        "sensor_size": "1/3 inch"
                    },
                    "caddx_nebula": {
                        "name": "Caddx Nebula",
                        "resolution": "720p",
                        "sensor_size": "1/3 inch"
                    }
                },
                "connection_types": {
                    "digital": {
                        "name": "Digital",
                        "protocols": ["DJI O3", "HDZero", "Walksnail Avatar"],
                        "typical_latency": "20-40ms"
                    },
                    "analog": {
                        "name": "Analog",
                        "protocols": ["5.8GHz", "2.4GHz", "1.3GHz"],
                        "typical_latency": "5-20ms"
                    }
                }
            }
        },
        "zir_bace": {
            "name": "Zir Bace",
            "description": "Base drone systems for copters with advanced capabilities",
            "subcategories": {
                "flight_controllers": {
                    "pixhawk": {
                        "name": "Pixhawk",
                        "variants": ["Pixhawk 4", "Pixhawk 6X", "Pixhawk Mini"],
                        "config_files": ["zir_bace_pixhawk_basic.cfg", "zir_bace_pixhawk_pro.cfg"]
                    },
                    "ardupilot": {
                        "name": "ArduPilot",
                        "variants": ["ArduCopter", "ArduPlane", "ArduRover"],
                        "config_files": ["zir_bace_ardupilot_standard.cfg", "zir_bace_ardupilot_premium.cfg"]
                    },
                    "naza": {
                        "name": "Naza-M",
                        "variants": ["Naza-M Lite", "Naza-M V2"],
                        "config_files": ["zir_bace_naza_light.cfg", "zir_bace_naza_pro.cfg"]
                    },
                    "dji_a3": {
                        "name": "DJI A3",
                        "variants": ["A3", "A3 Pro"],
                        "config_files": ["zir_bace_dji_a3_standard.cfg", "zir_bace_dji_a3_premium.cfg"]
                    },
                    "betaflight": {
                        "name": "Betaflight F4",
                        "variants": ["F4", "F7", "F405"],
                        "config_files": ["zir_bace_betaflight_sport.cfg", "zir_bace_betaflight_racing.cfg"]
                    },
                    "kiss": {
                        "name": "KISS FC",
                        "variants": ["KISS FC v1", "KISS FC v2", "KISS Ultra"],
                        "config_files": ["zir_bace_kiss_standard.cfg", "zir_bace_kiss_performance.cfg"]
                    }
                },
                "sizes": {
                    "micro": {
                        "name": "Micro",
                        "description": "Under 100mm frame size",
                        "weight_range": "50g-100g",
                        "typical_motors": "1102-1105"
                    },
                    "mini": {
                        "name": "Mini",
                        "description": "100-200mm frame size",
                        "weight_range": "100g-250g",
                        "typical_motors": "1306-2204"
                    },
                    "medium": {
                        "name": "Medium",
                        "description": "200-350mm frame size",
                        "weight_range": "250g-500g",
                        "typical_motors": "2205-2306"
                    },
                    "standard": {
                        "name": "Standard",
                        "description": "350-500mm frame size",
                        "weight_range": "500g-1000g",
                        "typical_motors": "2306-2807"
                    },
                    "large": {
                        "name": "Large",
                        "description": "500-650mm frame size",
                        "weight_range": "1000g-2000g",
                        "typical_motors": "3508-4108"
                    },
                    "xlarge": {
                        "name": "X-Large",
                        "description": "Over 650mm frame size",
                        "weight_range": "2000g+",
                        "typical_motors": "4114-6215"
                    }
                },
                "cameras": {
                    "sony_imx219": {
                        "name": "Sony IMX219",
                        "resolution": "3280×2464",
                        "sensor_size": "1/4 inch"
                    },
                    "sony_imx477": {
                        "name": "Sony IMX477",
                        "resolution": "4056×3040",
                        "sensor_size": "1/2.3 inch"
                    },
                    "gopro_hero9": {
                        "name": "GoPro Hero 9",
                        "resolution": "5120×2880",
                        "sensor_size": "1/2.3 inch"
                    },
                    "runcam_eagle": {
                        "name": "RunCam Eagle",
                        "resolution": "800TVL",
                        "sensor_size": "1/3 inch"
                    },
                    "foxeer_predator": {
                        "name": "Foxeer Predator",
                        "resolution": "1000TVL",
                        "sensor_size": "1/3 inch"
                    },
                    "dji_fpv": {
                        "name": "DJI FPV Camera",
                        "resolution": "1080p",
                        "sensor_size": "1/2.3 inch"
                    },
                    "caddx_vista": {
                        "name": "Caddx Vista",
                        "resolution": "720p",
                        "sensor_size": "1/3 inch"
                    },
                    "caddx_nebula": {
                        "name": "Caddx Nebula",
                        "resolution": "720p",
                        "sensor_size": "1/3 inch"
                    }
                },
                "connection_types": {
                    "digital": {
                        "name": "Digital",
                        "protocols": ["DJI O3", "HDZero", "Walksnail Avatar"],
                        "typical_latency": "20-40ms"
                    },
                    "analog": {
                        "name": "Analog",
                        "protocols": ["5.8GHz", "2.4GHz", "1.3GHz"],
                        "typical_latency": "5-20ms"
                    }
                }
            }
        },
        "zir_plane": {
            "name": "Zir Plane",
            "description": "Advanced fixed-wing aircraft systems",
            "subcategories": {
                "flight_controllers": {
                    "pixhawk": {
                        "name": "Pixhawk",
                        "variants": ["Pixhawk 4", "Pixhawk 6X", "Pixhawk Mini"],
                        "config_files": ["zir_plane_pixhawk_basic.cfg", "zir_plane_pixhawk_advanced.cfg"]
                    },
                    "ardupilot": {
                        "name": "ArduPilot",
                        "variants": ["ArduCopter", "ArduPlane", "ArduRover"],
                        "config_files": ["zir_plane_ardupilot_std.cfg", "zir_plane_ardupilot_premium.cfg"]
                    },
                    "naza": {
                        "name": "Naza-M",
                        "variants": ["Naza-M Lite", "Naza-M V2"],
                        "config_files": ["zir_plane_naza_basic.cfg"]
                    },
                    "dji_a3": {
                        "name": "DJI A3",
                        "variants": ["A3", "A3 Pro"],
                        "config_files": ["zir_plane_dji_a3_standard.cfg", "zir_plane_dji_a3_pro.cfg"]
                    },
                    "betaflight": {
                        "name": "Betaflight F4",
                        "variants": ["F4", "F7", "F405"],
                        "config_files": ["zir_plane_betaflight_sport.cfg", "zir_plane_betaflight_race.cfg"]
                    },
                    "kiss": {
                        "name": "KISS FC",
                        "variants": ["KISS FC v1", "KISS FC v2", "KISS Ultra"],
                        "config_files": ["zir_plane_kiss_standard.cfg"]
                    }
                },
                "aircraft_types": {
                    "fixed_wing": {
                        "name": "Fixed Wing",
                        "description": "Traditional airplane design",
                        "wing_span_range": "80-200cm",
                        "flight_characteristics": "Stable, efficient for long distances"
                    },
                    "flying_wing": {
                        "name": "Flying Wing",
                        "description": "Tailless fixed-wing aircraft",
                        "wing_span_range": "60-180cm",
                        "flight_characteristics": "Fast, agile, efficient"
                    },
                    "vtol": {
                        "name": "VTOL",
                        "description": "Vertical Take-Off and Landing",
                        "wing_span_range": "100-250cm",
                        "flight_characteristics": "Combines quadcopter and fixed-wing capabilities"
                    },
                    "glider": {
                        "name": "Glider",
                        "description": "Designed for soaring flight",
                        "wing_span_range": "150-300cm",
                        "flight_characteristics": "Excellent lift-to-drag ratio, long flight times"
                    },
                    "delta_wing": {
                        "name": "Delta Wing",
                        "description": "Triangular wing design",
                        "wing_span_range": "60-150cm",
                        "flight_characteristics": "Highly maneuverable, good for acrobatics"
                    }
                },
                "cameras": {
                    "sony_imx219": {
                        "name": "Sony IMX219",
                        "resolution": "3280×2464",
                        "sensor_size": "1/4 inch"
                    },
                    "sony_imx477": {
                        "name": "Sony IMX477",
                        "resolution": "4056×3040",
                        "sensor_size": "1/2.3 inch"
                    },
                    "gopro_hero9": {
                        "name": "GoPro Hero 9",
                        "resolution": "5120×2880",
                        "sensor_size": "1/2.3 inch"
                    },
                    "runcam_eagle": {
                        "name": "RunCam Eagle",
                        "resolution": "800TVL",
                        "sensor_size": "1/3 inch"
                    },
                    "foxeer_predator": {
                        "name": "Foxeer Predator",
                        "resolution": "1000TVL",
                        "sensor_size": "1/3 inch"
                    },
                    "dji_fpv": {
                        "name": "DJI FPV Camera",
                        "resolution": "1080p",
                        "sensor_size": "1/2.3 inch"
                    },
                    "caddx_vista": {
                        "name": "Caddx Vista",
                        "resolution": "720p",
                        "sensor_size": "1/3 inch"
                    },
                    "caddx_nebula": {
                        "name": "Caddx Nebula",
                        "resolution": "720p",
                        "sensor_size": "1/3 inch"
                    }
                },
                "connection_types": {
                    "digital": {
                        "name": "Digital",
                        "protocols": ["DJI O3", "HDZero", "Walksnail Avatar"],
                        "typical_latency": "20-40ms"
                    },
                    "analog": {
                        "name": "Analog",
                        "protocols": ["5.8GHz", "2.4GHz", "1.3GHz"],
                        "typical_latency": "5-20ms"
                    }
                }
            }
        }
    }
    
    return products_structure

def upload_to_firebase(db, products_structure):
    """Upload product categories and subcategories to Firebase Firestore"""
    products_collection = db.collection('products')
    
    # Upload each main category
    for category_id, category_data in products_structure.items():
        products_collection.document(category_id).set({
            "name": category_data["name"],
            "description": category_data["description"]
        })
        
        # Create subcollections for each subcategory type
        for subcategory_type, subcategories in category_data["subcategories"].items():
            subcollection_ref = products_collection.document(category_id).collection(subcategory_type)
            
            # Upload each subcategory
            for subcategory_id, subcategory_data in subcategories.items():
                subcollection_ref.document(subcategory_id).set(subcategory_data)
    
    print(f"Successfully uploaded product categories and subcategories to Firebase Firestore.")

def main():
    """Main function to generate and upload product structure"""
    # Generate fixed product structure
    print("Creating product category structure...")
    products_structure = generate_products_structure()
    
    # Initialize Firebase and upload data
    print("Initializing Firebase connection...")
    db = initialize_firebase()
    
    print("Uploading product structure to Firebase...")
    upload_to_firebase(db, products_structure)
    
    print("Product structure upload complete!")

if __name__ == "__main__":
    main()