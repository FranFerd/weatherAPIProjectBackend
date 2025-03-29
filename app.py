from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from functions.weather_service import Weather_service
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 30

jwt = JWTManager(app)
users = {
    "testuser": {
        "password" : "testpass"
    }
}

@app.route('/login', methods=["POST"])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"msg" : "Missing credentials"}), 400
    
    if username not in users or users[username]['password'] != password:
        return jsonify({"msg": "Bad credentials"}), 401
    
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

@app.route('/protected', methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/weather/current/<location>', methods = ["GET"])
def get_weather_current(location: str):
    return Weather_service(location).get_weather_current()

@app.route('/weather/today/hourly/<location>')
def get_weather_today_hourly(location: str):
    return Weather_service(location).get_weather_today_hourly()

@app.route('/weather/today/hourly/check-address/<location>')
def check_address(location: str):
    return Weather_service(location).check_address()

if __name__ == '__main__':
    app.run(debug=True)