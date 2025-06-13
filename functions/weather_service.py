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
        
    def get_weather_hourly(self, number_of_days):

        redis_key = 'weatherHourly' + self.location + str(number_of_days)
        cached_data = self._redis_client.get(redis_key)
        if cached_data:
            return json.loads(cached_data)
        
        url = f'{self.BASE_URL}/{self.location}'
        params = {
            "unitGroup" : "metric",
            "key" : self.__api_key,
            "include" : "hours,resolvedAddress",
            "elements": "address,datetime,temp,feelslike,conditions,preciptype,icon,windspeed,uvindex,sunrise,sunset",
            "content-type" : "json",
            "locationMode" : "single"
        }

        response = requests.get(url, params=params)
        response.raise_for_status() 
        weather_data_raw = response.json()
        weather_data_refined = {
            "address" : weather_data_raw.get("address"),
            "resolvedAddress" : weather_data_raw.get("resolvedAddress"),
            "days" : weather_data_raw.get("days")[:number_of_days]
        }

        self._redis_client.setex(name=redis_key, time=timedelta(seconds=3600) ,value=json.dumps(weather_data_refined))

        return weather_data_refined

        
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
            

