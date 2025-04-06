from dotenv import load_dotenv

import os
import redis
import json
from datetime import timedelta
import requests
from flask import jsonify


class Weather_service:
    load_dotenv()
    BASE_URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline' 

    def __init__(self, location):
        self.location = location
        self._redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.__api_key = os.getenv('API_KEY')

    def get_weather_current(self):
        redis_key = 'weatherCurrent' + self.location
        cached_data = self._redis_client.get(redis_key)
        if cached_data:
            return jsonify(json.loads(cached_data))
        url = f'{self.BASE_URL}/{self.location}'
        params = {
            "unitGroup" : "metric",
            "key" : self.__api_key,
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
            self._redis_client.setex(name=redis_key, time=timedelta(seconds=10), value=json.dumps(current_conditions_filtered) )

            return jsonify(current_conditions_filtered)
        except requests.exceptions.RequestException as e:
            return jsonify({"error" : str(e)}), 500
        
    def get_weather_today_hourly(self):

        redis_key = 'weatherTodayHourly' + self.location
        cached_data = self._redis_client.get(redis_key)
        if cached_data:
            return json.loads(cached_data)
        
        url = f'{self.BASE_URL}/{self.location}'
        params = {
            "unitGroup" : "metric",
            "key" : self.__api_key,
            "include" : "hours,resolvedAddress",
            "elements": "address,datetime,temp,feelslike,conditions,tempmax,tempmin,feelslikemax,feelslikemin,precipprob,preciptype,icon,humidity,windspeedmean,uvindex,sunrise,sunset,pressure",
            "content-type" : "json",
            "locationMode" : "single"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status() 
            weather_data = response.json()

            self._redis_client.setex(name=redis_key, time=timedelta(seconds=10) ,value=json.dumps(weather_data))

            return jsonify(weather_data)
        except requests.exceptions.RequestException as e:
            return jsonify({"error" : str(e)}), 500
        
    def check_address(self):

        redis_key = 'checkAddress' + self.location
        cached_data = self._redis_client.get(redis_key)
        if cached_data:
            return json.loads(cached_data)
        
        url = f'{self.BASE_URL}/{self.location}'
        params = {
            "unitGroup" : "metric",
            "key" : self.__api_key,
            "include" : "address,resolvedAddress",
            "elements": "addres,resolvedAddress",
            "content-type" : "json",
            "locationMode" : "single"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status() 
            weather_data = response.json()

            if not weather_data.get('address'):
                return jsonify({"message" : "Incorrect location"}), 400

            today_hourly_weather = weather_data.get('address')
            self._redis_client.setex(name=redis_key, time=timedelta(seconds=10) ,value=json.dumps(today_hourly_weather))

            return jsonify(today_hourly_weather)
        except requests.exceptions.HTTPError as e:
            return jsonify({"message" : "Incorrect location"}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"error" : str(e)}, {"message" : "Invalid location"}), 500
            

