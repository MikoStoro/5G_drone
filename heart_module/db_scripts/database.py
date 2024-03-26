import pymongo

'''
EXAMPLE ENTRY:
type: bt/zigbee
time: datetime
value: received data
status: delivered/awaiting
id jest generowane zawsze, automatycznie

'''

client = pymongo.MongoClient("localhost", 27017)
db = client.drone_db
print(db.name)
print("DATABASES:" + str(client.list_database_names()))


db.received_data
db.received_data.insert_one({"x": 10}).inserted_id
db.received_data.insert_one({"x": 8}).inserted_id
db.received_data.insert_one({"x": 11}).inserted_id
#print(db.received_data.find_one())


#print id of every obj
for item in db.received_data.find():
    print(item)


'''
#drop collection
db.received_data.drop()
'''


'''  
db.my_collection.create_index("x")
for item in db.my_collection.find().sort("x", pymongo.ASCENDING):
    print(item["x"])

[item["x"] for item in db.my_collection.find().limit(2).skip(1)]
'''