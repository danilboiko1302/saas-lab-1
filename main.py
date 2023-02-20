import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_weather(location, date):
    url_base_url = "http://api.weatherapi.com/v1/history.json"

    url_exclude = f"?key={key}&q={location}&dt={date}"

    url = f"{url_base_url}{url_exclude}"

    payload = {}
    headers = {}



    response = requests.request("GET", url, headers=headers, data=payload)


    data = json.loads(response.text)["forecast"]["forecastday"][0]

    pressure = 0
    counter = 0
    for x in data["hour"]:
      counter = counter + 1
      pressure = pressure + x["pressure_mb"]

    result = {
        "temp_c": data["day"]["avgtemp_c"],
        "wind_kph": data["day"]["maxwind_kph"],
        "pressure_mb": round(pressure/counter, 2),
        "humidity": data["day"]["avghumidity"]
    }

    return result


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: Python Saas.</h2></p>"


@app.route(
    "/weather",
    methods=["POST"],
def main_endpoint():
    start_dt = dt.datetime.now()
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    if json_data.get("requester_name") is None:
        raise InvalidUsage("requester_name is required", status_code=400)

    if json_data.get("location") is None:
        raise InvalidUsage("location is required", status_code=400)

    if json_data.get("date") is None:
        raise InvalidUsage("date is required", status_code=400)

    token = json_data.get("token")
    requester_name = json_data.get("requester_name")
    location = json_data.get("location")
    date = json_data.get("date")
    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)


    data = get_weather(location, date)

    result = {
        "requester_name": requester_name,
        "timestamp": dt.datetime.now().isoformat(),
        "location": location,
        "date": date,
        "weather": data,
    }

    return result