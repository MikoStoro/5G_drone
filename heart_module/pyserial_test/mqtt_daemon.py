import serial
import time
import send_command as comm
import paho.mqtt.client as mqtt
import threading
import mqtt_config as config

port_open = 0
#try until port eopens
while port_open == 0:
    try: 
        mp = serial.Serial("/dev/ttyUSB2")
        port_open = 1
    except:
        print('could not open port, retrying...')
        time.sleep(0.5)


read_buffer = ''
write_buffer = []
write_buffer_lock = threading.Lock()
mqtt_connected = 0


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    mqtt_publish(str(msg.topic), str(msg.payload))

flag_connected = 0
def on_connect(client, userdata, flags, rc):
   global flag_connected
   flag_connected = 1
   print("Connected with result code "+str(rc))
   client.subscribe("5gdrone/client/#")

def on_disconnect(client, userdata, rc):
   global flag_connected
   flag_connected = 0
   print("Disconnected with result code "+str(rc))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.connect("localhost", 1883, 60)
client.loop_start()
#To be addded later

write_buffer = ['at', 'ati', 'cops?']
address = config.get_address()
topics = config.get_topics()



def get_len(text:str):
    return str(len(text.encode()))

def enter_topics():
    with write_buffer_lock:
        for topic in topics:
            comm = 'AT+CMQTTSUBTOPIC=0,' #client index
            comm += get_len(topic) #Topic length
            comm += ',0' #QOS
            write_buffer.append(comm)
            write_buffer.append(topic)
        comm = 'AT+CMQTTSUB=0'
        write_buffer.append(comm)


def mqtt_init():
    with write_buffer_lock:
        comm = 'AT+CMQTTSTART'
        write_buffer.append(comm)
        comm = 'AT+CMQTTACCQ=0,5G_DRONE,0,3' #index,id,tcp,version
        write_buffer.append(comm)
        comm = 'AT+CMQTTCONNECT=0,tcp://' + str(address) + '60,0'
        write_buffer.append(comm)

def mqtt_publish(topic, data):
    with write_buffer_lock:
        comm = 'AT+CMQTTTOPIC=0,' + get_len(topic)
        write_buffer.append(comm)
        write_buffer.append(topic)
        comm = 'AT+CMQTTPAYLOAD=0,' + get_len(data)
        write_buffer.append(comm)
        write_buffer.append(data)
        comm = 'AT+CQMTTPUB=0,0,120'
        write_buffer.append(comm)

current_payload = None
current_topic = None


def process_command(line):
    split_line = line.split(':')
    command = split_line[0]
    parameters = []
    if len(split_line) > 1:
        parameters = split_line[1].strip().split(',')

    if command == '+COPS':
        print('got COPS response')
        print(parameters)

    elif command == '+CREG':
        print('got CREG response')
        print(parameters)

    elif command == '+CGREG':
        print('got CGREG response')
        print(parameters)

    elif command == '+CMQTTCONNECT':
        err_code = parameters[0]
        if(err_code == '0'):
            mqtt_connected = 1
            enter_topics()
        else:
            print('Connection failed!')
            mqtt_init()

    elif command == '+CMQTTNONET' or command == '+CMQTTCONNLOST':
        mqtt_connected = 0
        mqtt_init()

    elif command == '+CMQTTRXSTART':
        current_topic = None
        current_payload = None

    elif command == '+CMQTTRXTOPIC':
        if current_topic is None:
            current_topic = parameters[2]
        else:
            current_topic += parameters[2]

    elif command == '+CMQTTRXPAYLOAD':
        if current_payload is None:
            current_payload = parameters[2]
        else:
            current_payload += parameters[2]
    
    elif command == '+CMQTTRXEND':
        client.publish(current_topic, current_payload)
        
    else:
        print("Command not supported: " + command)

while(True):
    waiting = mp.in_waiting
    if(waiting > 0):
        #reading
        data = mp.read(1)
        read_buffer += data.decode()
        print(read_buffer) #DEBUG
        split_buffer = read_buffer.split('\r\n')
        if(len(split_buffer) > 1):
            for i in range(len(split_buffer)-1): #last line will be incomplete
                line = split_buffer[i]
                if(len(line)>0):
                    print('Line: ' + split_buffer[i])
                    process_command(split_buffer[i])
            read_buffer = split_buffer[-1] #leave only the incomplete command

    #Begin critical section
    new_write_buffer = []
    with write_buffer_lock:
        for line in write_buffer:
            try:
                comm.send_and_leave(line) #lines will always be supplied whole
            except:
                new_write_buffer.append(line)
        write_buffer = new_write_buffer #remove all successfully written lines
    #end critical section
    time.sleep(0.1)
        