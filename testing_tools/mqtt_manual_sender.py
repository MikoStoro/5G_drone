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

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
#client.on_log=on_log
client.connect("localhost", 1883, 60)
client.loop_start()


current_topic = "topic1"

while(True):
    if flag_connected != 1:
        print("connection lost...")
        time.sleep(1)
        client.reconnect()
        continue
    
    
    command = input('>')
    
    command = command.split("+")
    
    if len(command) < 2:
        print('error')
        continue
        
    if command[0] == 't':
        current_topic = command[1]
    if command[0] == 'p':
        client.publish(current_topic, command[1])
        
