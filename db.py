from pymongo import MongoClient

class Mongo:
    def __init__(self, client_url="mongodb://localhost:27017/", database="AI_MODEL", collection="chat_history"):
        self.client = MongoClient(client_url)
        self.database = self.client[database]
        self.collection = self.database[collection]

    def save_into_db(self, user_input, model_res):
        self.collection.insert_one(user_input)
        self.collection.insert_one(model_res)

    def get_history(self, model):
        return list(self.collection.find({"model": model}, {"_id": 0 , "model":0}))

