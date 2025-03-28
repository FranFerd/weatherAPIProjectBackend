from flask import Flask
from functions.weather_service import Weather_service
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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