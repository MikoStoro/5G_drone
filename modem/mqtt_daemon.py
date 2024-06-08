import serial
import time
import modem_utils as modem
import paho.mqtt.client as mqtt
import threading
import mqtt_config as config


port_open = 0
#try until port eopens
DEVICE = '/dev/ttyUSB2'


mp = modem.open_port(DEVICE)

read_buffer = ''
write_buffer = []
write_buffer_lock = threading.Lock()
mqtt_connected = 0


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    mqtt_publish(str(msg.topic), str(msg.payload))

flag_connected = 0
def on_connect(client, userdata, flags, rc, info):
   global flag_connected
   flag_connected = 1
   print("Connected with result code "+str(rc))
   client.subscribe("5gdrone/client/#")

def on_disconnect(client, userdata, rc):
   global flag_connected
   flag_connected = 0
   print("Disconnected with result code "+str(rc))



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


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.connect('localhost', 1883, 60)
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


class BufferItem:
    def __init__(self,command:str):
        self.command = command
        self.sent = False
        self.got_response = False
        
    def __str__(self):
        return self.command
        
class BufferCommand(BufferItem): 
    def __init__(self,command:str):
        self.command = command
        self.core = get_core_comm(command)
        self.got_response = False
        self.sent = False


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


def enter_topics():
    for topic in server_topics:
        enter_topic(topic)
        comm = 'AT+CMQTTSUB=0'
        write_command(comm)

def mqtt_init():
    comm = 'AT+CMQTTSTART'
    write_command(comm)
    comm = 'AT+CMQTTACCQ=0,"5G_DRONE",0,3' #index,id,tcp,version
    write_command(comm)
    comm = 'AT+CMQTTCONNECT=0,"tcp://' + str(server_address) + '",60,0'
    if server_uname is not None and server_password is not None:
        comm += ',"' + server_uname + '","' + server_password + '"'
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


awaiting_response_data = None

def process_response(line):
    global write_buffer
    global current_topic
    global current_payload
    global awaiting_response_data
        
    print("Received:" + line + " " + str(awaiting_response_data))
    

    if ('=' or '?') in line:
        print("Not a valid response")
        return
    try:
        split_line = line.split(':')
        command = split_line[0].split("+")[1]
        parameters = []
        simple_line=False
        
    except:
        command = line
        simple_line = True

    #mark item that got the response
    '''for item in write_buffer:
        if type(item) is BufferCommand:
            comm : BufferCommand = item
            #print("Comm core: " + command + " buffer_core: " + comm.core)
            if comm.core == command and not comm.got_response:
                print(command + 'got response!')
                comm.got_response = True
                break'''
                
    for item in write_buffer:
        if type(item) is BufferCommand:
            comm : BufferCommand = item
            if line == 'OK' or line =='ERROR':
                print(str(comm) + 'got response! ' + line)
                comm.got_response = True
                break

    print(str(awaiting_response_data))
    
    if not simple_line and len(split_line) > 1:
        parameters = split_line[1].strip().split(',')

    if command == 'COPS':
        print('got COPS response')
        print(parameters)

    elif command == 'CREG':
        print('got CREG response')
        print(parameters)

    elif command == 'CGREG':
        print('got CGREG response')
        print(parameters)

    elif command == 'CMQTTCONNECT':
        err_code = parameters[0]
        if(err_code == '0'):
            mqtt_connected = 1
            enter_topics()
        else:
            print('Connection failed!')
            clear_buffer()
            mqtt_init()

    elif command == '+CMQTTNONET' or command == '+CMQTTCONNLOST':
        mqtt_connected = 0
        mqtt_init()

    elif command == 'CMQTTRXSTART':
        current_topic = None
        current_payload = None

    elif command == 'CMQTTRXTOPIC':
        awaiting_response_data = 'topic'
        print("AWAITING RESPONSE DATA: TOPIC")

    elif command == 'CMQTTRXPAYLOAD':
        awaiting_response_data = 'payload'
        print("AWAITING RESPONSE DATA: PAYLOAD")
    
    elif command == 'CMQTTRXEND':
        if(current_payload is not None and current_topic is not None):
            print("SENDING " + current_payload + "TO TOPIC" + current_topic)
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
                
        
        print("Command not supported: " + command)

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
    already_waiting = False
    with write_buffer_lock:
        awaiting_data = False
        if '>' in read_buffer:
            awaiting_data = True
            print('AWAITING DATA')
        
        
        if len(write_buffer) >= 1: #send comm or data
            item = write_buffer[0]
            #print("trying to send item:"  + str(item))
            if type(item) is BufferCommand:
                #print("we have a command here")
                if item.sent == False:
                    print("sending " + str(item))
                    modem.send_and_leave(mp,item.command) 
                    item.sent = True
            elif item.sent == False and awaiting_data:
                print("sending " + str(item))
                modem.send_and_leave(mp,item.command)
                item.sent = True
                item.got_response = True
        
        if len(write_buffer) >= 2:
            item = write_buffer[1]
            if type(item) is not BufferCommand and item.sent == False and awaiting_data:
                modem.send_and_leave(mp,item.command)
                print("sending " + str(item))
                item.sent = True
                item.got_response = True
                
        
        
        '''for line in write_buffer:
            if type(line) is BufferCommand:
                command : BufferCommand  = line 
                if command.got_response == False and command.sent == True:
                    if not already_waiting:
                        print("1 already waiting")
                        already_waiting = True
                    else:
                        print("BREAKING")
                        break
            
            item : BufferItem = line
            try:
                print("sending: " + item.command)
                comm.send_and_leave(item.command) #lines will always be supplied whole
                item.sent = True
                already_waiting = True
            except Exception as e:
                print(e)'''
         
        #remove all successfully written lines
        write_buffer[:] = [ x for x in write_buffer if (x.got_response == False)]
        #end critical section
        time.sleep(0.25)
        
