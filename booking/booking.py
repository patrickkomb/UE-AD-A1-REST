from flask import Flask, request, jsonify, make_response
import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.permissions import admin_required, owner_or_admin_required
from repository import get_repository
from env import SCHEDULE_SERVICE_URL, MOVIES_SERVICE_URL

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

repo = get_repository()

@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings/<userid>", methods=['GET'])
@owner_or_admin_required
def get_bookings_for_user(userid):
    bookings = repo.load()
    for user_booking in bookings:
        if user_booking["userid"] == userid:
            return make_response(jsonify(user_booking), 200)
    return make_response(jsonify({"error": "No bookings for this user"}), 404)

@app.route("/bookings/<userid>", methods=['POST'])
@owner_or_admin_required
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
    bookings = repo.load()
    for user_booking in bookings:
        if user_booking["userid"] == userid:
            # Search if the date already exists for this user
            for booking_date in user_booking["dates"]:
                if booking_date["date"] == date:
                    if movie in booking_date["movies"]:
                        return make_response(jsonify({"error": "Already booked"}), 409)
                    booking_date["movies"].append(movie)
                    repo.save(bookings)
                    return make_response(jsonify({"message": "booking added"}), 200)
            # Date not found, add new date with movie
            user_booking["dates"].append({
                "date": date,
                "movies": [movie]
            })
            repo.save(bookings)
            return make_response(jsonify({"message": "booking added"}), 200)

    bookings.append({
        "userid": userid,
        "dates": [{"date": date, "movies": [movie]}]
    })
    repo.save(bookings)
    return make_response(jsonify({"message": "booking added"}), 200)

@app.route("/bookings/<userid>", methods=['DELETE'])
@owner_or_admin_required
def delete_booking(userid):
    req = request.get_json()
    date = req.get("date")
    movie = req.get("movie")
    if not date or not movie:
        return make_response(jsonify({"error": "Missing date or movie"}), 400)

    bookings = repo.load()
    for user_booking in bookings:
        if user_booking["userid"] == userid:
            for booking_date in user_booking["dates"]:
                if booking_date["date"] == date and movie in booking_date["movies"]:
                    booking_date["movies"].remove(movie)
                    if not booking_date["movies"]:
                        user_booking["dates"].remove(booking_date)
                    repo.save(bookings)
                    return make_response(jsonify({"message": "booking deleted"}), 200)
    return make_response(jsonify({"error": "Booking not found"}), 404)

@app.route("/bookings/movie/<movie_id>", methods=['GET'])
@admin_required
def get_users_for_movie(movie_id):
    # Check if movie exists with Movie service
    try:
        movie_resp = requests.get(f"{MOVIES_SERVICE_URL}/{movie_id}")
        if movie_resp.status_code != 200:
            return make_response(jsonify({"error": "Movie ID not found"}), 404)
        movie_detail = movie_resp.json()
    except Exception as e:
        return make_response(jsonify({"error": "Movie service unavailable: {str(e)}"}), 503)

    users = []
    bookings = repo.load()
    for user_booking in bookings:
        for booking_date in user_booking["dates"]:
            if movie_id in booking_date["movies"]:
                users.append({
                    "userid": user_booking["userid"],
                    "date": booking_date["date"]
                })

    if not users:
        return make_response(jsonify({
            "movie": movie_detail,
            "error": "No bookings found for this movie"
        }), 404)

    return make_response(jsonify({
        "movie": movie_detail,
        "users": users
    }), 200)


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
