from flask import Flask, jsonify
import requests
from functions.weather_service import Weather_service
from dotenv import load_dotenv
import os
import redis
import json
from datetime import timedelta

load_dotenv()


app = Flask(__name__)

@app.route('/weather/current/<location>', methods = ["GET"])
def get_weather_current(location: str):
    return Weather_service(location).get_weather_current()

    
@app.route('/weather/today/hourly/<location>')
def get_weather_today_hourly(location: str):
    return Weather_service(location).get_weather_today_hourly()
# def get_weather_today_hourly(location: str):

#     redis_key = 'weatherTodayHourly' + location
#     cached_data = redis_client.get(redis_key)
#     if cached_data:
#         return json.loads(cached_data)
    
#     url = f'{BASE_URL}/{location}'
#     params = {
#         "unitGroup" : "metric",
#         "key" : API_key,
#         "include" : "hours",
#         "elements": "datetime,temp,feelslike,conditions,tempmax,tempmin,feelslikemax,feelslikemin,precipprob,preciptype"
#     }

#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         weather_data = response.json()

#         today_hourly_weather = weather_data.get('days')[0]
#         redis_client.setex(name=redis_key, time=timedelta(seconds=10) ,value=json.dumps(today_hourly_weather))

#         return jsonify(today_hourly_weather)
#     except requests.exceptions.RequestException as e:
#         return jsonify({"error" : str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)