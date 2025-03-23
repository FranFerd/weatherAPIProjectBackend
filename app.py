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
redis_client = redis.Redis(host='localhost', port=6379, db=0)
API_key = os.getenv("API_KEY")
BASE_URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline'

@app.route('/weather/<location>')
def get_weather_test(location):
    url = f'{BASE_URL}/{location}'
    params = {
        "unitGroup" : "metric",
        "key" : API_key,
        "include" : "hours",
        "elements": "datetime,temp,feelslike,conditions,tempmax,tempmin,feelslikemax,feelslikemin,precipprob,preciptype"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        weather_data = response.json()

        current_conditions = weather_data.get('currentConditions')

        return jsonify(weather_data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error" : str(e)}), 500

@app.route('/weather/current/<location>', methods = ["GET"])
def get_weather_current(location):

    redis_key = 'weatherCurrent' + location
    cached_data = redis_client.get(redis_key)
    if cached_data:
        return jsonify(json.loads(cached_data))
    
    url = f'{BASE_URL}/{location}'
    params = {
        "unitGroup" : "metric",
        "key" : API_key,
        "include" : "current",
        "elements": "datetime,temp,feelslike,conditions,tempmax,tempmin,feelslikemax,feelslikemin,precipprob,preciptype"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        weather_data = response.json()

        current_conditions = weather_data.get('currentConditions')

        current_conditions_filtered = {
            "Current_time" : current_conditions.get('datetime'),
            "temperature" : current_conditions.get('temp'),
            "feels_like" : current_conditions.get('feelslike'),
            "description" : current_conditions.get('conditions'),
            "precipitation_probability" : current_conditions.get('precipprob'),
            "precipitation_type" : current_conditions.get('preciptype')
        }
        redis_client.setex(name=redis_key, time=timedelta(seconds=10), value=json.dumps(current_conditions_filtered) )

        return jsonify(current_conditions_filtered)
    except requests.exceptions.RequestException as e:
        return jsonify({"error" : str(e)}), 500
    
@app.route('/weather/today/hourly/<location>')
def get_weather_today_hourly(location):

    redis_key = 'weatherTodayHourly' + location
    cached_data = redis_client.get(redis_key)
    if cached_data:
        return json.loads(cached_data)
    
    url = f'{BASE_URL}/{location}'
    params = {
        "unitGroup" : "metric",
        "key" : API_key,
        "include" : "hours",
        "elements": "datetime,temp,feelslike,conditions,tempmax,tempmin,feelslikemax,feelslikemin,precipprob,preciptype"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        weather_data = response.json()

        today_hourly_weather = weather_data.get('days')[0]
        redis_client.setex(name=redis_key, time=timedelta(seconds=10) ,value=json.dumps(today_hourly_weather))

        return jsonify(today_hourly_weather)
    except requests.exceptions.RequestException as e:
        return jsonify({"error" : str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)