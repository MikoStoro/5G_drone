import serial
import time
import modem_utils as modem
import paho.mqtt.client as mosquitto
import threading
import mqtt_config as config


port_open = 0
#try until port reopens
DEVICE = '/dev/ttyUSB2'


mp = modem.open_port(DEVICE)

read_buffer = ''
write_buffer = []
write_buffer_lock = threading.Lock()
mqtt_connected = 0

def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))

def on_message(mosq, obj, msg):
	global mqtt_connected
	if(mqtt_connected == 1):
		mqtt_publish(str(msg.topic), msg.payload.decode())
		#print(msg.topic + str(msg.qos) + " " + str(msg.payload))
	else:
		print("not connected!")

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(string)

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


write_buffer = []
'''#address = "10.111.1.54:1883"
server_address = "cow.rmq2.cloudamqp.com"
server_topics = ['a','b','c']
server_uname = "vtzciybt:vtzciybt"
server_password = "b_F7I3JHJVgw9LdVcJ8zL6zTheLb0-6Z"
#address = config.get_address()
#topics = config.get_topics()
'''
cfg = config.get_config()
print(cfg)
server_address = cfg['address']
server_topics = cfg['topics']
server_uname = cfg['login']
server_password = cfg['password']


client = mosquitto.Client(mosquitto.CallbackAPIVersion.VERSION1)
client.on_message = on_message
client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe

#Uncomment to enable debug messages
#client.on_log = on_log

client.connect("localhost", 1883)
client.subscribe("5gdrone/client/#", 0)
client.loop_start()



def get_core_resp(comm:str):
    comm = str(comm).split("+")
    if len(comm) > 1:
        return comm[1].split(":")[0]
    else: return comm[0].split(":")[0]

def get_core_comm(comm:str):
    comm = str(comm).split("+")
    if len(comm) > 1:
        return comm[1].split("=")[0]
    else: return comm[0].split("=")[0]

        
class BufferCommand(): 
    def __init__(self,command:str, data = None):
        self.command = command
        self.core = get_core_comm(command)
        self.got_response = False
        self.sent = False
        self.data = data
        #print("CREATED BUFFER COMMAND: " + str(command) + " " + str(data))
    
    def __str__(self):
        return self.command


def write_command(command: str, data: str = None):
    with write_buffer_lock:
	    write_buffer.append(BufferCommand(command, data))

def get_len(text:str):
    return str(len(text.encode()))

def clear_buffer():
    write_buffer.clear()

def enter_topic(topic):
    comm = 'AT+CMQTTSUBTOPIC=0,' #client index
    comm += get_len(topic) #Topic length
    comm += ',0' #QOS
    write_command(comm, topic)


def enter_topics():
    for topic in server_topics:
        enter_topic(topic)
        comm = 'AT+CMQTTSUB=0'
        write_command(comm)

def mqtt_init():
    global mqtt_connected
    comm = 'AT+CMQTTSTART'
    write_command(comm)
    comm = 'AT+CMQTTACCQ=0,"5G_DRONE",0,4' #index,id,tcp,version
    write_command(comm)
    comm = 'AT+CMQTTCONNECT=0,"tcp://' + str(server_address) + '",60,0'
    if server_uname is not None and server_password is not None:
        comm += ',"' + server_uname + '","' + server_password + '"'
    write_command(comm)
    enter_topics()
    mqtt_connected = 1

def mqtt_publish(topic, data):
    comm = 'AT+CMQTTTOPIC=0,' + get_len(topic)
    write_command(comm, topic)
    comm = 'AT+CMQTTPAYLOAD=0,' + get_len(data)
    write_command(comm, data)
    comm = 'AT+CMQTTPUB=0,0,120'
    write_command(comm)

current_payload = None
current_topic = None


awaiting_response_data = None
current_command = None


def process_response(line):
    global write_buffer
    global current_topic
    global current_payload
    global awaiting_response_data
    global current_command
        
 

    print(line)
    if ('=' or '?') in line:
        #print("Not a valid response\n")
        return
    try:
        split_line = line.split(':')
        command = split_line[0].split("+")[1]
        parameters = []
        simple_line=False
    except:
        command = line
        simple_line = True
                

    if (line == 'OK' or line =='ERROR') and current_command is not None:
        print((str(current_command) + ' got response: ' + line + '\n'))
        current_command.got_response = True
        current_command = None
        return

    if(awaiting_response_data is not None):
        print(str(awaiting_response_data))
    
    if not simple_line and len(split_line) > 1:
        parameters = split_line[1].strip().split(',')


    elif command == 'CMQTTCONNECT':
        err_code = parameters[1]
        '''if(err_code == '0' or err_code == '23'):
            enter_topics()
            time.sleep(1)
            mqtt_connected = 1
        else:
            print('Connection failed!')
            clear_buffer()
            mqtt_init()'''

    elif command == 'CMQTTNONET' or command == 'CMQTTCONNLOST':
        mqtt_connected = 0
        mqtt_init()

    elif command == 'CMQTTRXSTART':
        current_topic = None
        current_payload = None
	
    elif command == 'CMQTTACCQ':
        time.sleep(1)

    elif command == 'CMQTTRXTOPIC':
        awaiting_response_data = 'topic'
        print("AWAITING RESPONSE DATA: TOPIC")

    elif command == 'CMQTTRXPAYLOAD':
        awaiting_response_data = 'payload'
        print("AWAITING RESPONSE DATA: PAYLOAD")
    
    elif command == 'CMQTTRXEND':
        if(current_payload is not None and current_topic is not None):
            print("SENDING " + current_payload + " TO TOPIC " + current_topic)
            client.publish(current_topic, current_payload)
        
    else:

        if awaiting_response_data is not None:
                
            print("COMMAND:" + command)
    
            if awaiting_response_data == 'topic':
                if current_topic is None:
                    current_topic = command
                else:
                    current_topic += command
                print("TOPIC IS NOW: " +current_topic)
            if awaiting_response_data == 'payload':
                if current_payload is None:
                    current_payload = command
                else:
                    current_payload += command
                print("PAYLOAD IS NOW: " +current_payload)
            awaiting_response_data = None
            
mqtt_init()


while(True):
    waiting = mp.in_waiting
    if(waiting > 0):
        #reading
        waiting_bytes = mp.in_waiting
        data = mp.read(waiting_bytes)
        read_buffer += data.decode()
        #print("state of the read buffer: " + read_buffer) #DEBUG
        split_buffer = read_buffer.split('\r\n')
        if(len(split_buffer) > 1):
            for i in range(len(split_buffer)-1): #last line will be incomplete
                line = split_buffer[i]
                if(len(line)>0):
                    process_response(split_buffer[i])
            read_buffer = split_buffer[-1] #leave only the incomplete command

        
    #Begin critical section
    with write_buffer_lock:
        if '>' in read_buffer:
            modem.send_and_leave(mp,(current_command.data)) 
        
		
        if len(write_buffer) >= 1:
            item = write_buffer[0]
            if current_command is None:
                modem.send_and_leave(mp,item.command) 
                current_command = item
                item.sent = True
        
        

        write_buffer[:] = [ x for x in write_buffer if (x.got_response == False)]
        #end critical section
    time.sleep(0.15)
        
