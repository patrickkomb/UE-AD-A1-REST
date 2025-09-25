import requests
from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3202
HOST = '0.0.0.0'
MOVIES_SERVICE_URL = 'http://localhost:3200/movies'

with open('{}/databases/times.json'.format("."), "r") as jsf:
   schedules = json.load(jsf)["schedule"]

def write(times):
   with open('{}/databases/times.json'.format("."), 'w') as f:
      full = {'schedule': times}
      json.dump(full, f)

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"

@app.route("/schedules/<date>", methods=['GET'])
def get_schedule_bydate(date):
    for schedule in schedules:
        if str(schedule["date"]) == str(date):
            res = make_response(jsonify(schedule),200)
            return res
    return make_response(jsonify({"error":"No schedule for this date"}),404)

@app.route("/schedules/<date>/movies", methods=['GET'])
def get_schedule_details_bydate(date):
    for schedule in schedules:
        if str(schedule["date"]) == str(date):
            movies = []
            for movie in schedule["movies"]:
                movie_resp = requests.get(f"{MOVIES_SERVICE_URL}/{movie}")
                if movie_resp.status_code == 200:
                    movie_detail = movie_resp.json()
                    movies.append(movie_detail)

            if movies:
                return make_response(jsonify({
                    "date": date,
                    "movies": movies
                }), 200)

            return make_response(jsonify({
                "date": date,
                "error": "No movies found for this schedule"
            }), 404)

    return make_response(jsonify({"error": "No schedule for this date"}), 404)

@app.route("/schedules", methods=['POST'])
def add_schedule():
    req = request.get_json()

    for schedule in schedules:
        if str(schedule["date"]) == str(req["date"]):
            print(schedule["date"])
            print(req["date"])
            return make_response(jsonify({"error":"Schedule date already exists"}),409)

    schedules.append(req)
    write(schedules)
    res = make_response(jsonify({"message":"schedule added"}),200)
    return res

@app.route("/schedules/<date>", methods=['DELETE'])
def del_schedule_bydate(date):
    for schedule in schedules:
        if str(schedule["date"]) == str(date):
            schedules.remove(schedule)
            write(schedules)
            return make_response(jsonify(schedule),200)

    res = make_response(jsonify({"error":"Schedule date not found"}),404)
    return res

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
