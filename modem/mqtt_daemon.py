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

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.connect("localhost", 1883, 60)
client.loop_start()

write_buffer = []
#address = "10.111.1.54:1883"
server_address = "cow.rmq2.cloudamqp.com"
server_topics = ['a','b','c']
server_uname = "vtzciybt:vtzciybt"
server_password = "b_F7I3JHJVgw9LdVcJ8zL6zTheLb0-6Z"
#address = config.get_address()
#topics = config.get_topics()
##TODO: add password and uname to config file


def get_core(comm:str):
    return comm.split("+")[1].split("=")[0]


class BufferItem:
    def __init__(self,command:str):
        self.command = command
        self.sent = False
class BufferCommand(BufferItem): 
    def __init__(self,command:str):
        self.command = command
        self.core = get_core(command)
        self.got_response = False
        self.sent = False

write_buffer.append(BufferCommand("ati"))
write_buffer.append(BufferCommand("cops"))


def write_command(command: str):
    write_buffer.append(BufferCommand(command))

def write_data(data: str):
    write_buffer.append(BufferItem(data))

def get_len(text:str):
    return str(len(text.encode()))

def clear_buffer():
    write_buffer.clear()

def enter_topic(topic):
    comm = 'AT+CMQTTSUBTOPIC=0,' #client index
    comm += get_len(topic) #Topic length
    comm += ',0' #QOS
    write_command(comm)
    write_data(topic)
    comm = 'AT+CMQTTSUB=0'
    write_command(comm)

def enter_topics():
    for topic in server_topics:
        enter_topic(topic)

def mqtt_init():
    comm = 'AT+CMQTTSTART'
    write_command(comm)
    comm = 'AT+CMQTTACCQ=0,"5G_DRONE",0,3' #index,id,tcp,version
    write_command(comm)
    comm = 'AT+CMQTTCONNECT=0,"tcp://' + str(server_address) + '",60,0'
    if server_uname is not None and server_password is not None:
        comm += ',' + server_uname + ',' + server_password
    write_command(comm)

def mqtt_publish(topic, data):
    comm = 'AT+CMQTTTOPIC=0,' + get_len(topic)
    write_command(comm)
    write_data(topic)
    comm = 'AT+CMQTTPAYLOAD=0,' + get_len(data)
    write_command(comm)
    write_data(data)
    comm = 'AT+CQMTTPUB=0,0,120,0,0'
    write_command(comm)

current_payload = None
current_topic = None


def process_response(line):
    split_line = line.split(':')
    command = split_line[0]
    parameters = []
    core = get_core(line)
    
    
    #mark item that got the response
    for item in write_buffer:
        if type(item) is BufferCommand:
            comm = BufferCommand(item)
            if comm.core == core and not comm.got_response:
                comm.got_response = True
                break
                
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

mqtt_init()
enter_topics()

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
                    process_response(split_buffer[i])
            read_buffer = split_buffer[-1] #leave only the incomplete command

        
    #Begin critical section
    already_waiting = False
    with write_buffer_lock:
        for line in write_buffer:
            if type(line) is BufferCommand:
                command  = BufferCommand(line)
                if not command.got_response:
                    if not already_waiting: already_waiting = True
                    else: break
            
            item = BufferItem(line)
            try:
                comm.send_and_leave(item.command) #lines will always be supplied whole
                item.sent = True
            except:
               break
         
        #remove all successfully written lines
        write_buffer[:] = [x for x in write_buffer if not BufferItem(x).sent]
    #end critical section
    time.sleep(0.1)
        