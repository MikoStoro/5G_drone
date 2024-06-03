import paho.mqtt.client as mqtt
import ast

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("ble/device/data")

def on_message(client, userdata, msg):
    print("Message received on topic: ", msg.topic)
    try:
        payload = msg.payload.decode('utf-8')
        data = ast.literal_eval(payload)  # Safely evaluate the string to a dictionary
        print("Received data: ", data)
        # Process the data as needed
    except Exception as e:
        print("Failed to decode message: ", e)
    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

client.loop_forever()
