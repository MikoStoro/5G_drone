
import paho.mqtt.client as mqtt
import ast
import time
import random
from guizero import App,TextBox

dict={
    "wiadomosc"
    "ustawienia"
    "dane"
}

flag_conected = 0
def process_payload(payload, encoding='utf-8'):
    decoded=payload.decode(encoding)
    data=None
    try:
        data=ast.literal_eval(decoded)
    except:
        data=decoded
    return data
    
def on_connect(client, userdata, flags, rc):
    global flag_conected
    flag_conected = 1
    print("Connected with result code "+str(rc))
    client.subscribe("5gdrone/client/data")

def on_message(client,userdata,msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_start()

app=App()

tresc=TextBox(app)


app.display()
