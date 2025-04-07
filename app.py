from flask import Flask, jsonify, send_from_directory, Response, request
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask_cors import CORS
import os
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from gridfs import GridFS
import re 
from dotenv import load_dotenv

app = Flask(__name__, static_folder='static')
CORS(app)

# MongoDB Configuration

load_dotenv()
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
client = MongoClient(app.config["MONGO_URI"], server_api=ServerApi('1'))
db = client["ecommerce"]
collection = db["products"]
users_collection = client["credentials"]["users"]
fs = GridFS(db)

# Utility function to convert ObjectId to string
def mongo_to_dict(mongo_obj):
    mongo_obj["_id"] = str(mongo_obj["_id"]) 
    return mongo_obj

# Load initial file
@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.errorhandler(404)
def page_not_found(error):
    return send_from_directory('static', '404.html'), 404

@app.route('/login')
def login():
    return send_from_directory('static', 'login.html')

@app.route('/login-form', methods=['POST'])
def login_form():
    print("in login form")
    data = request.get_json()

    email = data['email']
    password = data['password']
    user = users_collection.find_one({"email": email})
    
    if not user:
        print("no user")
        return jsonify({"error": "User not found. Please sign up!"}), 400

    # Validate password
    if not check_password_hash(user["password"], password):
        print("password error")
        return jsonify({"error": "Invalid password!"}), 400

    # Create session (if using sessions)
    # session["user_id"] = str(user["_id"])
    print("Login successful!")

    return jsonify({"message": "Login successful!"}), 200


@app.route('/signup')
def signup():
    return send_from_directory('static', 'signup.html')

@app.route('/signup-form', methods=['POST']) 
def signup_form():
    # Get the data from the incoming JSON
    data = request.get_json()

    username = data['fullname']
    dob = data['dob']
    email = data['email']
    password = data['password']
    confirm_password = data['confirm-password']

    # Check if the email is already taken
    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already exists!"}), 400

    # Check if passwords match
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match!"}), 400

    # Check for strong password (minimum 8 characters, 1 uppercase, 1 lowercase, 1 digit)
    password_pattern = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[A-Z]).{8,}$')
    if not password_pattern.match(password):
        return jsonify({"error": "Password must be at least 8 characters, with at least one uppercase letter, one lowercase letter, and one digit!"}), 400

    # Hash the password before saving
    hashed_password = generate_password_hash(password)

    # Create user document
    user_data = {
        "username": username,
        "dob": dob,
        "email": email,
        "password": hashed_password
    }

    # Insert user data into MongoDB
    try:
        users_collection.insert_one(user_data)
        return jsonify({"message": "Account created successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/products', methods=['GET'])
def get_products():
    products = collection.find()
    product_list = [
        mongo_to_dict({
            "name": product["name"],
            "description": product["description"],
            "price": product["price"],
            "image": f"/image/{str(product['image'])}",
            "_id": product["_id"]
        })
        for product in products
    ]
    return jsonify(product_list)

@app.route('/image/<image_id>', methods=['GET'])
def get_image(image_id):
    try:
        # Fetch image from GridFS using the ObjectId
        image_id = ObjectId(image_id)  # Convert string back to ObjectId
        file = fs.get(image_id)  # Get the file from GridFS
        
        # Detect the MIME type based on the file extension or header (you may use python-magic for this)
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension == 'jpg' or file_extension == 'jpeg':
            mimetype = 'image/jpeg'
        elif file_extension == 'png':
            mimetype = 'image/png'
        else:
            mimetype = 'application/octet-stream'  # Default MIME type for unknown files

        return Response(file.read(), mimetype=mimetype)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)