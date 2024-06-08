import paho.mqtt.client as mqtt
import ast
import time
import random
import datetime
from guizero import App,TextBox,Text,PushButton,Window


flag_conected = 0
def process_payload(payload, encoding='utf-8'):
    decoded=payload.decode(encoding)
    print(decoded)
    data=None
    try:
        data=ast.literal_eval(decoded)
        return data
    except:
        data=decoded
        return data
    
def on_connect(client, userdata, flags, rc):
    global flag_conected
    flag_conected = 1
    print("Connected with result code "+str(rc))
    client.subscribe("5gdrone/client/data")
    client.subscribe("5gdrone/client/settings")

def on_message(client,userdata,msg):
    if(msg.topic=="5gdrone/client/settings"):
        global settings
        settings=process_payload(msg.payload)
    elif(msg.topic=="5gdrone/client/data"):
        print(msg.topic+" "+str(msg.payload))
        data=process_payload(msg.payload)
        print(type(data))
        id = data['_id']
        resposne= "confirm " + str(id)
        tresc.value += str(data['time']) + " " + str(data['type']) + '\n'
        wyswietl(data)
        zapisz_do_pliku(data)
        client.publish("5gdrone/heart/command",resposne)
        

def on_disconnect(client, userdata, rc):
   global flag_connected
   flag_connected = 0
   print("Disconnected with result code "+str(rc))
    
def wyswietl(data):
    x=data['value']
    for key,value in x.items():
        tresc.value+='\t' + str(key) + " " + str(value) + '\n'

def ustawienia():
    window2=Window(app)
    window2.show()
    czas=TextBox(window2)
    dane=TextBox(window2)
    wifi=TextBox(window2)
    for key,value in settings.items():
        if(key=="tiemout"):
            czas.value=value
        elif(key=="db_size"):
            dane.value=value
        elif(key=="wifi"):
            wifi.value=value
    wyslij=PushButton(window2,text="Wyslij",command=lambda:wyslanie(czas,dane,wifi))

def wyslanie(czas,dane,wifi):
    settings["timeout"]=czas.value
    settings["db_size"]=dane.value
    settings["wifi"]=wifi.value
    client.publish("5gdrone/client/settings",str(settings))
    print("tu"+str(settings))


def zapisz_do_pliku(data):
    czas=datetime.datetime.now()
    nazwa = czas.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
    with open(nazwa,'w') as plik:
        plik.write(str(tresc.value))

def laczenie():
    window.show()
    adres_box = TextBox(window)
    port_box = TextBox(window)
    button3=PushButton(window,align="bottom", text="Polacz",command=lambda:polacz(adres_box,port_box))
    print("tu")

def polacz(adres_box,port_box):
    print(str(adres_box.value))
    print(str(port_box.value))
    adres=str(adres_box.value)
    port=int(port_box.value)
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        client.connect(adres, port, 60)
        client.loop_start() 
    except:
        informacja=Text(window,text="zle dane",align="top")
    
def wyczysc():
    tresc.clear()
    

app=App(title="Client app",width=800,height=500)
window=Window(app,width=200, height=150)
window.hide()
tresc=TextBox(app,multiline=True, scrollbar=True,width="50",height="fill",align="right")
button1 = PushButton(app,align="top",text="wyczysc",command=wyczysc)
button2=PushButton(app,align="top",text="polacz",command=laczenie)
button3 =PushButton(app,align="top",text="ustawienia",command=ustawienia)
settings={"tiemout":5,"db_size":1000,"wifi":0}
try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.connect("localhost", 1883, 60)
    client.loop_start()
    client.publish("5gdrone/heart/command","get_settings")
except:
    informacja=Text(app,text="Nie udalo sie podlaczyc",align="top")
button4=PushButton(app,text="sent all",command=client.publish("5gdrone/heart/command","resent_all"))  

app.display()