import pymongo
from pymongo import MongoClient


def get_database():
    CONNECTION_STRING = "mongodb://root:root@10.1.0.229:27017/python?authSource=admin&w=majority&readPreference=primary&appname=MongoDB%20Compass&retryWrites=true&ssl=false"
    client = MongoClient(CONNECTION_STRING)
    db = client["python"]
    collection = db["test"]
    item_1 = {
        "item_name": "Blender",
        "max_discount": "10%",
        "batch_number": "RR450020FRG",
        "price": 340,
        "category": "kitchen appliance",
    }
    data = collection.insert_one(item_1)
    print(data)


""" def create_collection():
    dbname = get_database()
    collection_name = dbname["smart_flows2"]
    item_1 = {
        "_id": "U1IT00001",
        "item_name": "Blender",
        "max_discount": "10%",
        "batch_number": "RR450020FRG",
        "price": 340,
        "category": "kitchen appliance",
    }
    collection_name.insert_many([item_1]) çç∫"""

get_database()
