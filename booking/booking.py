from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'
SCHEDULE_SERVICE_URL = 'http://localhost:3202/schedules'

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
   bookings = json.load(jsf)["bookings"]

def write(bookings_list):
   with open('{}/databases/bookings.json'.format("."), 'w') as f:
      full = {'bookings': bookings_list}
      json.dump(full, f)

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings/<userid>", methods=['GET'])
def get_bookings_for_user(userid):
    for user_booking in bookings:
        if user_booking["userid"] == userid:
            return make_response(jsonify(user_booking), 200)
    return make_response(jsonify({"error": "No bookings for this user"}), 404)

@app.route("/bookings/<userid>", methods=['POST'])
def add_booking(userid):
    req = request.get_json()
    date = req.get("date")
    movie = req.get("movie")
    if not date or not movie:
        return make_response(jsonify({"error": "Missing date or movie"}), 400)

    # Check if movie is scheduled on this date (with Schedule service)
    try:
        sched_resp = requests.get(f"{SCHEDULE_SERVICE_URL}/{date}")
        if sched_resp.status_code != 200:
            return make_response(jsonify({"error": "Date not found in schedule"}), 404)
        schedule = sched_resp.json()
        if movie not in schedule.get("movies", []):
            return make_response(jsonify({"error": "Movie not scheduled this date"}), 400)
    except Exception as e:
        return make_response(jsonify({"error": f"Schedule service unavailable: {str(e)}"}), 503)

    # Search if user already exists in bookings
    for user_booking in bookings:
        if user_booking["userid"] == userid:
            # Search if the date already exists for this user
            for booking_date in user_booking["dates"]:
                if booking_date["date"] == date:
                    if movie in booking_date["movies"]:
                        return make_response(jsonify({"error": "Already booked"}), 409)
                    booking_date["movies"].append(movie)
                    write(bookings)
                    return make_response(jsonify({"message": "booking added"}), 200)
            # Date not found, add new date with movie
            user_booking["dates"].append({
                "date": date,
                "movies": [movie]
            })
            write(bookings)
            return make_response(jsonify({"message": "booking added"}), 200)

    bookings.append({
        "userid": userid,
        "dates": [{"date": date, "movies": [movie]}]
    })
    write(bookings)
    return make_response(jsonify({"message": "booking added"}), 200)

@app.route("/bookings/<userid>", methods=['DELETE'])
def delete_booking(userid):
    req = request.get_json()
    date = req.get("date")
    movie = req.get("movie")
    if not date or not movie:
        return make_response(jsonify({"error": "Missing date or movie"}), 400)

    for user_booking in bookings:
        if user_booking["userid"] == userid:
            for booking_date in user_booking["dates"]:
                if booking_date["date"] == date and movie in booking_date["movies"]:
                    booking_date["movies"].remove(movie)
                    if not booking_date["movies"]:
                        user_booking["dates"].remove(booking_date)
                    write(bookings)
                    return make_response(jsonify({"message": "booking deleted"}), 200)
    return make_response(jsonify({"error": "Booking not found"}), 404)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
