import json
from pymongo import MongoClient
from env import USE_MONGO, MONGO_URL

SCHEDULE_FILE = "{}/databases/times.json"

def get_repository():
    if USE_MONGO:
        return MongoScheduleRepository()
    return JsonScheduleRepository()

class JsonScheduleRepository:
    def load(self):
        with open(SCHEDULE_FILE.format("."), "r") as file:
            return json.load(file)["schedule"]

    def save(self, schedules):
        with open(SCHEDULE_FILE.format("."), "w") as file:
            json.dump({"schedule": schedules}, file)

class MongoScheduleRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client.get_database()
        self.collection = self.db["schedules"]

        # Data initialization from JSON if empty collection
        if self.collection.count_documents({}) == 0:
            json_repo = JsonScheduleRepository()
            self.collection.insert_many(json_repo.load())

    def load(self):
        return list(self.collection.find({}, {"_id": 0}))

    def save(self, schedules):
        self.collection.delete_many({})
        if schedules:
            self.collection.insert_many(schedules)
