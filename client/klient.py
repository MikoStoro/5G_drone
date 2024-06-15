import paho.mqtt.client as mqtt
import ast
import time
import random
import datetime
from guizero import App,TextBox,Text,PushButton,Window


flag_conected = 0
def process_payload(payload, encoding='utf-8'):
    data = payload
    if type(payload) is not str:
        data=payload.decode(encoding)
        print(data)
    try:
        data=ast.literal_eval(data)
        print('value: ' + data['value'])
        return data
    except:
        print('eval failed')
        return data
    
def on_connect(client, userdata, flags, rc):
    global flag_conected
    flag_conected = 1
    print("Connected with result code "+str(rc))
    client.subscribe("5gdrone/client/data")
    client.subscribe("5gdrone/client/settings")

def display_entry(data):
    tresc.value += str(data['time']) + " " + str(data['type']) + '\n'
    value = data['value']
    try:
        value_dict = ast.literal_eval(value)
        for key,value in value_dict.items():
            tresc.value+='\t' + str(key) + " " + str(value) + '\n'
    except:
        tresc.value+='\t' + value + '\n'
	

def on_message(client,userdata,msg):

    payload = msg.payload
    if(msg.topic=="5gdrone/client/settings"):
        global settings
        settings=process_payload(payload)
    elif(msg.topic=="5gdrone/client/data"):
        print(msg.topic+" "+str(payload))
        data=process_payload(msg.payload)
        print(type(data))
        if(type(data) is dict):
            id = data['_id']
            resposne= "confirm " + str(id)
            client.publish("5gdrone/heart/command",resposne)
            display_entry(data)
        zapisz_do_pliku(data)

        

def on_disconnect(client, userdata, rc):
   global flag_connected
   flag_connected = 0
   print("Disconnected with result code "+str(rc))
    
def wyswietl(data):
    print(type(data))
    
    
    if type(data) is dict:
        for key,value in data.items():
            tresc.value+='\t' + str(key) + " " + str(value) + '\n'
    else:
        tresc.value+='\t' + data + '\n'
		
		
def ustawienia():
    window2=Window(app)
    window2.show()
    czas=TextBox(window2)
    dane=TextBox(window2)
    wifi=TextBox(window2)
    for key,value in settings.items():
        if(key=="resend_timeout"):
            czas.value=value
        elif(key=="max_db_size"):
            dane.value=value
        elif(key=="wifi"):
            wifi.value=value
    wyslij=PushButton(window2,text="Wyslij",command=lambda:wyslanie(czas,dane,wifi))

def wyslanie(czas,dane,wifi):
    settings["resend_timeout"]=czas.value
    settings["max_db_size"]=dane.value
    settings["wifi"]=wifi.value
    client.publish("5gdrone/heart/settings",str(settings))
    client.publish("5gdrone/heart/settings",str(settings))
    print("tu"+str(settings))


def zapisz_do_pliku(data):
    czas=datetime.datetime.now()
    nazwa = czas.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
    with open(nazwa,'w') as plik:
        plik.write(str(tresc.value))

def laczenie():
    window.show()
    adres_label = Text(window, text="Adres")
    adres_box = TextBox(window)
    adres_box.value = "cow.rmq2.cloudamqp.com"
    port_label = Text(window, text="Port")
    port_box = TextBox(window)
    port_box.value = '1883'
    
    login_label = Text(window, text="Login")
    login_box = TextBox(window)
    login_box.value = "vtzciybt:vtzciybt"
    password_label = Text(window, text="Hasło")
    password_box = TextBox(window)
    password_box.value = "b_F7I3JHJVgw9LdVcJ8zL6zTheLb0-6Z"
    
    button3=PushButton(window,align="bottom", text="Polacz",command=lambda:polacz(adres_box,port_box,login_box,password_box))
    
    print("tu")

def polacz(adres_box,port_box,login_box,password_box):
    print(str(adres_box.value))
    print(str(port_box.value))
    adres=str(adres_box.value)
    port=int(port_box.value)
    login=str(login_box.value)
    password=str(password_box.value)
    
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        if len(login)>0 and len(password)>0:
            client.username_pw_set(login, password)
        client.connect(adres, port, 60)
        client.loop_start() 
    except:
        informacja=Text(window,text="zle dane",align="top")
    
def wyczysc():
    tresc.clear()
    

app=App(title="Client app",width=800,height=500)
window=Window(app,width=200, height=150)
window.hide()
tresc=TextBox(app,multiline=True, scrollbar=True,width="75",height="fill",align="right")
button1 = PushButton(app,align="top",text="wyczysc",command=wyczysc)
button2=PushButton(app,align="top",text="polacz",command=laczenie)
button3 =PushButton(app,align="top",text="ustawienia",command=ustawienia)
settings={"resend_timeout":5,"max_db_size":1000,"wifi":0}
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
button4=PushButton(app,text="Prześlij ponownie",command=client.publish("5gdrone/heart/command","resend_all"))  

app.display()
