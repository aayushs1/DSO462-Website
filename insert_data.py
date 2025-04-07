from pymongo import MongoClient
from pymongo.server_api import ServerApi
from gridfs import GridFS
from bson import ObjectId
import os
from dotenv import load_dotenv

# MongoDB Configuration
load_dotenv()
uri = os.getenv("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["ecommerce"]
collection = db["products"]

# Set up GridFS to handle file uploads
fs = GridFS(db)

# Directory where the images are stored on your local machine
image_dir = 'images/'

sample_products = [
    {
        "name": "iPhone 16 Pro Max",
        "description": "Apple's most advanced iPhone with A18 Pro chip and titanium design.",
        "price": 1199,
        "image": "iphone_16_pro_max.jpg"
    },
    {
        "name": "MacBook Air M4",
        "description": "Apple’s thin and powerful laptop with M4 chip and Liquid Retina display.",
        "price": 1299,
        "image": "macbook_m4_air.jpg"
    },
    {
        "name": "Sony WH-1000XM5",
        "description": "Industry-leading noise canceling headphones with 30 hours of battery life.",
        "price": 399,
        "image": "sony_xm5.jpg"
    },
    {
        "name": "Apple Watch Series 9",
        "description": "Apple's latest smartwatch with blood oxygen monitoring and ECG features.",
        "price": 399,
        "image": "apple_watch_s10.jpg"
    },
    {
        "name": "iPad Air M2",
        "description": "Apple's lightweight and powerful tablet with M2 chip and Apple Pencil support.",
        "price": 699,
        "image": "apple_ipad_m2.jpg"
    },
    {
        "name": "PlayStation 5",
        "description": "Sony’s next-gen gaming console with 4K gaming and ultra-fast SSD.",
        "price": 499,
        "image": "ps5.jpg"
    },
    {
        "name": "Canon EOS R6 Mark II",
        "description": "Professional mirrorless camera with 24.2MP sensor and 4K 60p video recording.",
        "price": 2499,
        "image": "canon.jpeg"
    },
    {
        "name": "Bose SoundLink Revolve+",
        "description": "Portable Bluetooth speaker with 360-degree sound and deep bass.",
        "price": 299,
        "image": "bose.jpg"
    },
    {
        "name": "LG 27” 4K UHD Monitor",
        "description": "LG UltraFine 27-inch monitor with HDR and USB-C connectivity.",
        "price": 649,
        "image": "lg_monitor.jpg"
    },
    {
        "name": "Logitech MX Mechanical Keyboard & MX Master 3S Mouse",
        "description": "Ergonomic mechanical keyboard and precision wireless mouse for professionals.",
        "price": 199,
        "image": "mx-keys-s-combo.png"
    }
]

# Function to upload image file to GridFS
def upload_image(image_filename):
    with open(os.path.join(image_dir, image_filename), 'rb') as img_file:
        file_data = img_file.read()
    # Save image to GridFS
    file_id = fs.put(file_data, filename=image_filename)
    return file_id

# Insert Data into MongoDB and upload images
for product in sample_products:
    image_filename = product["image"]
    file_id = upload_image(image_filename)
    product["image"] = file_id  # Store the file_id instead of the image path

# Insert data into the MongoDB collection
collection.insert_many(sample_products)

print("Sample data inserted successfully!")