import paho.mqtt.client as mqtt
import ast
import pymongo
import datetime
import time

##CONFIG
settings={
    "resend_timeout" : 1, #10 s
    "max_db_size" : 1000000 #1 MB
}
resend_time = None

##END CONFIG

##STATE

##END STATE


TYPE_BT=0
TYPE_ZB=1

ST_RECIEVED=0
ST_DELIVERED=1

bt_topic = "bluetooth"
zb_topic= "zigbee2mqtt"

db_client = pymongo.MongoClient("localhost", 27017)
db = db_client.drone_db
'''
    EXAMPLE ENTRY:
    type: bt/zigbee
    time: datetime
    value: received data
    status: delivered/awaiting
    id jest generowane zawsze, automatycznie
'''



def send_data(data):
    try:
        #data = str(data)
        strid = str(data["_id"])
        data["_id"] = strid
        data = str(data)
        print("sending " + data)
        client.publish('5gdrone/client/data', payload=str(data))
    except:
        print("ERROR while sending data: cannot cast to string!")
   

def get_entry_type(topic):
    return topic[2]

def resend_data():
    now = datetime.datetime.now()
    for item in db.received_data.find():
        if item['status'] != ST_DELIVERED:
            print(item['time'])
            item_time = datetime.datetime.fromisoformat(item['time'])
            time_diff = now - item_time
            #if(time_diff > resend_time):
            send_data(item)
    pass

def get_db_size():
    stats = db.command('dbstats')
    return stats['dataSize']

def process_command(data):
    data = data.split(' ')
    if(data[0] == 'resend_all'):
        resend_data()
    elif(data[0] == 'confirm'):
        confirm_id = data[1]
        mark_delivered(confirm_id)
    else:
        print("unknown command")



def push_entry(data, topic):
    entry_time = datetime.datetime.now()
    entry_type = get_entry_type(topic)
    entry_value = str(data)
    entry_status = ST_RECIEVED
    entry = {"time" : str(entry_time),
             "type" : entry_type,
             "value" : str(entry_value),
             "status" : entry_status}
    entry_id = db.received_data.insert_one(entry).inserted_id
    print("inserted " + str(entry_id))
    print("curent size: " + str(get_db_size()))
    return entry_id

def mark_delivered(id):
    new_value={"$set" : {"status":ST_DELIVERED}}
    db.received_data.update_one({"_id" : id}, new_value, upsert=False)
    pass

def process_payload(payload, encoding='utf-8'):
    decoded=payload.decode(encoding)
    data=None
    try:
        data=ast.literal_eval(decoded)
        return data
    except:
        data=decoded
        return data

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("5gdrone/heart/#")

def get_time_from_seconds(val):
    seconds = val % 60
    val = val // 60
    if(val == 0):
        return(datetime.time(second=seconds))

    minutes = val %60
    val = val//60
    if(val == 0):
        return(datetime.time(second=seconds, minute=minutes))
    
    hours = val % 24
    val = val//24
    if(val == 0):
        return(datetime.time(hour=hours, minute=minutes, second=seconds))
    else:
        raise ValueError("Timeout cannotg be longer than 24 hours!")


    pass 

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    data = process_payload(msg.payload)
    topic = msg.topic.split('/')
    
    ##select action based on topic
    if(topic[2] in [bt_topic, zb_topic]):
        push_entry(data, topic)

    elif(topic[2] == 'test'): 
        push_entry(data, topic)
    elif(topic[2] == 'command'):
        print("received command:" + str(data))
        process_command(data)
    elif(topic[2] == 'settings'):
        print("settings updated: " + str(data))
    else:
        print("Unsupported topic: " + str(topic[2]))

    #for testing reasons
    for item in db.received_data.find():
        print(item)
    

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_start()

resend_time = get_time_from_seconds(settings["resend_timeout"])


while True:
    time.sleep(settings['resend_timeout'])
    #the mqtt client thread will carry out all db operations, to make synchronizarion easier
    client.publish("5gdrone/heart/command", "resend_all")
