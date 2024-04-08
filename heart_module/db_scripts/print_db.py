import pymongo
client = pymongo.MongoClient("localhost", 27017)
db = client.drone_db
for item in db.received_data.find():
    print(item)