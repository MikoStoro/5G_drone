import serial
import time

port = "/dev/ttyUSB2"

def convert_to_comm(text):
	text += '\r\n'
	text = text.encode()
	return text

def response_to_text(response):
	lines = response.decode().split('\r\n')
	return lines

def wait_till_end(mp):
	waiting_prev = mp.in_waiting
	waiting_curr = mp.in_waiting
	diff = -1
	while not diff == 0:
		time.sleep(0.01)
		waiting_prev = waiting_curr
		waiting_curr = mp.in_waiting
		diff = waiting_curr - waiting_prev
	return



def send_command(text):
	mp = serial.Serial(port)
	
	command = convert_to_comm(text)
	mp.write(command)
	
	#time.sleep(0.1)
	wait_till_end(mp)	
	waiting = mp.in_waiting
	data = mp.read(waiting)
	return response_to_text(data)



def send_and_leave(comm, args = []):
	mp = serial.Serial(port)
	comm = comm + ','.join(args)
	command = convert_to_comm(comm)
	mp.write(command)
	return
	



MQTT_START = 'AT+CMQTTSTART'
MQTT_STOP = 'AT+CMQTTSTOP'
MQTT_CLIENT = 'AT+CMQTTACCQ'


print(send_command('at'))

print(send_command('ati'))