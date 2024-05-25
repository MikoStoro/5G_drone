import serial
import time
import send_command as comm
import paho.mqtt.client as mqtt
import threading

port_open = 0
#try until port eopens
while port_open == 0:
    try: 
        mp = serial.Serial("/dev/ttyUSB2")
        port_open = 1
    except:
        print('could not open port, retrying...')
        time.sleep(0.5)




def get_core(comm:str):
    return comm.split("+")[1].split("=")[0]

class BufferCommand: 
    def __init__(self,command:str):
        self.command = command
        self.core = get_core(command)
        self.got_response = False

write_buffer = ['at', 'ati', 'cops?']
address = "10.111.1.54:1883"


def write_command(command: str):
    write_buffer.append(BufferCommand(command))

def write_data(data: str):
    write_buffer.append(data)

def get_len(text:str):
    return str(len(text.encode()))

def enter_topic(topic):
    comm = 'AT+CMQTTSUBTOPIC=0,' #client index
    comm += get_len(topic) #Topic length
    comm += ',0' #QOS
    write_command(comm)
    write_data(topic)
    comm = 'AT+CMQTTSUB=0'
    write_command(comm)



def mqtt_init():
    comm = 'AT+CMQTTSTART'
    write_command(comm)
    comm = 'AT+CMQTTACCQ=0,"5G_DRONE",0,3' #index,id,tcp,version
    write_command(comm)
    comm = 'AT+CMQTTCONNECT=0,"tcp://' + str(address) + '",60,0'
    write_command(comm)

def mqtt_publish(topic, data):
    comm = 'AT+CMQTTTOPIC=0,' + get_len(topic)
    write_command(comm)
    write_data(topic)
    comm = 'AT+CMQTTPAYLOAD=0,' + get_len(data)
    write_command(comm)
    write_data(data)
    comm = 'AT+CQMTTPUB=0,0,120'
    write_command(comm)

current_payload = None
current_topic = None


while(True):
    command = input()
    comand = command.split(" ")
    
    if command != "":
        if command[0] == 't':
            enter_topic(command[1])

        if command[0] == 'p':
            mqtt_publish(comand[1], command[2])   

        if command[0] == 'i':
            mqtt_init()

    new_write_buffer = []
    for line in write_buffer:
        if type(line) is BufferCommand:
            if not BufferCommand(line).got_response:
                
        print(comm.send_command(line)) #lines will always be supplied whole
        write_buffer = write_buffer[1:]
        time.sleep(0.2)