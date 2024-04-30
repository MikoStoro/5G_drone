import serial
import time
import send_command as comm
import paho.mqtt.client as mqtt
import threading

connected = 0
#try until port eopens
while connected == 0:
    try: 
        mp = serial.Serial("/dev/ttyUSB2")
        connected = 1
    except:
        time.sleep(0.5)


read_buffer = ''
write_buffer = []


'''
write_buffer_lock = threading.Lock()

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
client.connect("localhost", 1883, 60)
client.loop_start()
#To be addded later
'''
write_buffer = ['at', 'ati', 'cops?']


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
            read_buffer = split_buffer[-1] #leave only the incomplete command

    #Begin critical section
    new_write_buffer = []
    for line in write_buffer:
        try:
            comm.send_and_leave(line) #lines will always be supplied whole
        except:
            new_write_buffer.append(line)
    write_buffer = new_write_buffer #remove all successfully written lines
    #end critical section
    time.sleep(0.1)
        