from flask import Flask, jsonify
import requests
from functions.weather_service import Weather_service


app = Flask(__name__)

API_key = '4MS79AXVEU9ANQ6ULBZ3J6JGS'
BASE_URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline'

@app.route('/weather/<location>', methods = ["GET"])
def get_weather(location):
    url = f'{BASE_URL}/{location}'
    params = {
        "unitGroup" : "metric",
        "key" : API_key,
        "include" : "current,hours",
        "elements": "datetime,temp,feelslike,conditions,tempmax,tempmin,feelslikemax,feelslikemin,precipprob,preciptype"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        weather_data = response.json()
        current_conditions = weather_data.get('currentConditions')

        filtered_data = {
            "Current_time" : current_conditions.get('datetime'),
            "temperature" : current_conditions.get('temp'),
            "feels_like" : current_conditions.get('feelslike'),
            "description" : current_conditions.get('conditions')
        }
        return jsonify(weather_data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error" : str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)