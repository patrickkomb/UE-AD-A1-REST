from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

with open('{}/databases/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

def write(users):
    with open('{}/databases/users.json'.format("."), 'w') as f:
        full = {'users': users}
        json.dump(full, f)

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users/<userid>", methods=['GET'])
def get_user_byid(userid):
    for user in users:
        if str(user["id"]) == str(userid):
            res = make_response(jsonify(user),200)
            return res
    return make_response(jsonify({"error":"User ID not found"}),404)

@app.route("/users", methods=['POST'])
def add_user():
    req = request.get_json()

    for user in users:
        if str(user["id"]) == str(req["id"]):
            print(user["id"])
            print(req["id"])
            return make_response(jsonify({"error":"User ID already exists"}),409)

    users.append(req)
    write(users)
    res = make_response(jsonify({"message":"user added"}),200)
    return res

@app.route("/users/<userid>", methods=['PUT'])
def update_user(userid):
    req = request.get_json()

    for user in users:
        if str(user["id"]) == str(userid):
            user = req
            res = make_response(jsonify(user),200)
            write(users)
            return res

    res = make_response(jsonify({"error":"user ID not found"}),404)
    return res

@app.route("/users/<userid>", methods=['DELETE'])
def del_user(userid):
    for user in users:
        if str(user["id"]) == str(userid):
            users.remove(user)
            write(users)
            return make_response(jsonify(user),200)

    res = make_response(jsonify({"error":"user ID not found"}),404)
    return res

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
