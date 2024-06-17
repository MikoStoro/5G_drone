import random
import paho.mqtt.client as mqtt
import time

# def on_log(client, userdata, level, buf):
#     print("log: ",buf)

flag_connected = 0
def on_connect(client, userdata, flags, rc):
   global flag_connected
   flag_connected = 1
   print("Connected with result code "+str(rc))

def on_disconnect(client, userdata, rc):
   global flag_connected
   flag_connected = 0
   print("Disconnected with result code "+str(rc))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
#client.on_log=on_log
client.connect("localhost", 1883, 60)
client.loop_start()

while(True):
    if flag_connected == 1:
        # Publish message
        message = random.randbytes(random.randint(4,32))
        client.publish("5gdrone/heart/bluetooth", str({'key1' : 123, 'key2' : 456}))
        time.sleep(random.randint(1,4))
        message = random.randbytes(random.randint(4,32))
        client.publish("5gdrone/heart/zigbee2mqtt", "abcdef")
        time.sleep(random.randint(1,4))
    else:
        # Wait to reconnect
        time.sleep(5)
        client.reconnect()