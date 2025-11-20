import json
from pymongo import MongoClient
from env import USE_MONGO, MONGO_URL

MOVIES_FILE = "{}/databases/movies.json"

def get_repository():
    if USE_MONGO:
        return MongoMovieRepository()
    return JsonMovieRepository()

class JsonMovieRepository:
    def load(self):
        with open(MOVIES_FILE.format("."), "r") as file:
            return json.load(file)["movies"]

    def save(self, movies):
        with open(MOVIES_FILE.format("."), "w") as file:
            json.dump({"movies": movies}, file)

class MongoMovieRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client.get_database()
        self.collection = self.db["movies"]

        # Data initialization from JSON if empty collection
        if self.collection.count_documents({}) == 0:
            json_repo = JsonMovieRepository()
            self.collection.insert_many(json_repo.load())

    def load(self):
        return list(self.collection.find({}, {"_id": 0}))

    def save(self, movies):
        self.collection.delete_many({})
        if movies:
            self.collection.insert_many(movies)
