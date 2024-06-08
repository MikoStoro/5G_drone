import serial
import time

port = "/dev/ttyUSB2"

def open_port():
	mp_inner = None
	port_open = False
    
	while port_open == False:
		try:
			mp_inner = serial.Serial("/dev/ttyUSB2")
			
			read = ''
			while(len(read) == 0):
				print('port open, not responding yet...')
				modem_utils.send_and_leave(mp_inner, 'at')
				read = mp_inner.read(mp_inner.in_waiting)
				print(read)
				time.sleep(1)
			port_open = True
			
		except Exception as e:
			print('could not open port for configuration, retrying...')
			print(e)
			port_open = 0
			time.sleep(1)
			
	return mp_inner

def convert_to_comm(text):
	text += '\r\n'
	if type(text) is str:
		text = text.encode()
	return text

def response_to_text(response):
	lines = response.decode().split('\r\n')
	return lines


def read_response(mp):
	time.sleep(0.25)
	return(response_to_text(mp.read(mp.in_waiting)))

def send_and_wait(mp, text):
	mp = serial.Serial(port)
	
	command = convert_to_comm(text)
	mp.write(command)
	
	data = read_response(mp)
	return response_to_text(data)



def send_and_leave(serial, comm, args = []):
	comm = str(comm) + ','.join(args)
	command = convert_to_comm(comm)
	serial.write(command)
	return
