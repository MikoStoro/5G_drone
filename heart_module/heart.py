import paho.mqtt.client as mqtt
import ast
import pymongo
import datetime

TYPE_BT=0
TYPE_ZB=1

ST_RECIEVED=0
ST_DELIVERED=1

db_client = pymongo.MongoClient("localhost", 27017)

'''
EXAMPLE ENTRY:
type: bt/zigbee
time: datetime
value: received data
status: delivered/awaiting
id jest generowane zawsze, automatycznie
'''

def get_entry_type(topic):
    if topic == '':
        pass

def push_entry():

    pass

def change_status():
    
    pass

def process_payload(payload, encoding='utf-8'):
    decoded=payload.decode(encoding)
    data=None
    try:
        data=ast.literal_eval(decoded)
    except:
        data=decoded
    return data

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("5gdrone/#")



# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    print(process_payload(msg.payload))
    topic = msg.topic.split('/')
    
    ##select action based on topic
    if(topic[1] in ['bluetooth', 'zigbee2mqtt']):
        pass
    elif(topic[1] == 'test'): 
        push_entry()
    else:
        print("Unsupported option")
    
    entry_time = datetime.datetime.now()
    print(curr_time)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()