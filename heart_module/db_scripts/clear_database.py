import pymongo
client = pymongo.MongoClient("localhost", 27017)
db = client.drone_db
db.received_data.drop()
print("Cleared database!")