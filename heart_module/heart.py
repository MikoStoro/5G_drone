import paho.mqtt.client as mqtt
import ast
import datetime
import time
from tinydb import TinyDB, Query
import os
import heart_config 
import sys


ST_RECIEVED=0
ST_DELIVERED=1

disable_ap = 'sudo systemctl disable dnsmasq && sudo systemctl disable hostapd'
enable_ap = 'sudo systemctl enable dnsmasq && sudo systemctl enable hostapd'
connect_modem = 'sudo ' + sys.path[0] + '../modem/connect_modem.sh'
disconnect_modem = 'sudo '

##CONFIG
cfg = heart_config.get_config()

sensor_topics = cfg['sensor_topics']


settings = cfg['settings']
##END CONFIG

##STATE

##END STATE


db_path = 'drone.json'
db = TinyDB(db_path)
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
        print("sending" + str(data))
        client.publish('5gdrone/client/data', payload=str(data))
    except:
        print("ERROR while sending data: cannot cast to string!")
   

def get_entry_type(topic):
    return topic[2]

def resend_data():
    now = datetime.datetime.now()
    for item in db:
        if item['status'] != ST_DELIVERED:
            print(item['time'])
            item_time = datetime.datetime.fromisoformat(item['time'])
            time_diff = now - item_time
            if(time_diff > resend_time):
                send_data(item)
    pass

def get_db_size():
    return os.path.getsize(db_path)

def clear_sent():
    query = Query().status == ST_DELIVERED
    #deleted = db.received_data.delete_many(query)
    deleted = db.remove(query)
    print("deleted " + str(deleted) + " entries")

def process_command(data):
    data = data.split(' ')
    if(data[0] == 'resend_all'):
        resend_data()
    elif(data[0] == 'confirm'):
        confirm_id = data[1]
        mark_delivered(confirm_id)
    elif(data[0] == 'clear_sent'):
        clear_sent()
    else:
        print("unknown command")

def get_sendable_doc(identifier):
    doc = db.get(doc_id=identifier)
    print(doc)
    doc['_id'] = identifier
    print(doc['_id'])
    return doc

def push_entry(data, topic):
    entry_time = datetime.datetime.now()
    entry_type = get_entry_type(topic)
    entry_value = str(data)
    entry_status = ST_RECIEVED
    entry = {"time" : str(entry_time),
             "type" : entry_type,
             "value" : str(entry_value),
             "status" : entry_status}
    #entry_id = db.received_data.insert_one(entry).inserted_id
    entry_id = db.insert(entry)
    print("inserted " + str(entry_id))
    
    #
    db.update({'_id' : entry_id}, doc_ids=[int(entry_id)]) 
    
    size = get_db_size()
    print("curent size: " + str(size))
    if(size > settings["max_db_size"]):
        client.publish("5gdrone/heart/command", "clear_sent")
    return entry_id

def get_entry(identifier):
    return db.get(doc_id=identifier)

def mark_delivered(identifier):
    print("confirming: " + identifier)
    
    #new_value={"$set" : {"status":ST_DELIVERED}}
    #db.received_data.update_one({"_id" : ObjectId(identifier)}, new_value)
    db.update({'status' : ST_DELIVERED}, doc_ids=[int(identifier)]) 
    


def process_payload(payload, encoding='utf-8'):
    decoded=payload.decode(encoding)
    data=None
    try:
        data=ast.literal_eval(decoded)
        return data
    except:
        data=decoded
        return data

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("5gdrone/heart/#")

def get_time_from_seconds(val):
    seconds = val % 60
    val = val // 60
    if(val == 0):
        return(datetime.timedelta(seconds=seconds))

    minutes = val %60
    val = val//60
    if(val == 0):
        return(datetime.timedelta(seconds=seconds, minutes=minutes))
    
    hours = val % 24
    val = val//24
    if(val == 0):
        return(datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds))
    else:
        raise ValueError("Timeout cannot be longer than 24 hours!")


    pass 

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    data = process_payload(msg.payload)
    topic = msg.topic.split('/')
    
    ##select action based on topic
    if(topic[2] in [bt_topic, zb_topic]):
        entry_id = push_entry(data, topic)
        send_data(get_entry(entry_id))
    elif(topic[2] == 'test'): 
        entry_id = push_entry(data, topic)
        send_data(get_entry(entry_id))
    elif(topic[2] == 'command'):
        print("received command:" + str(data))
        process_command(data)
    elif(topic[2] == 'settings'):
        print("settings updated: " + str(data))
    else:
        print("Unsupported topic: " + str(topic[2]))

    #for testing reasons
    for item in db:
        print(item)
    

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_start()

resend_time = get_time_from_seconds(settings["resend_timeout"])


timer = 0
while True:
    #reset every 24h
    if timer>=86400:
        timer = 0

    time.sleep(1)
    timer += 1
    if(timer % settings['resend_timeout'] == 0):
        #the mqtt client thread will carry out all db operations, to make synchronizarion easier
        print("sending resend command")
        client.publish("5gdrone/heart/command", "resend_all")
