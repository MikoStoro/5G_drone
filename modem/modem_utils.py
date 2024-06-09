import serial
import time

port = "/dev/ttyUSB2"



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
	return data



def send_and_leave(serial, comm, args = []):
	comm = str(comm) + ','.join(args)
	command = convert_to_comm(comm)
	serial.write(command)
	return


def hard_reset(dev = None):
	if dev is None:
		dev = port
	mp = open_port(dev)
	send_and_leave('at+cusbcfg=usbid,1e0e,9011')
	mp = open_port(dev)
	send_and_leave('at+cusbcfg=usbid,1e0e,9001')

def open_port(device):
	mp_inner = None
	port_open = False
    
	while port_open == False:
		try:
			mp_inner = serial.Serial(device)
			
			read = ''
			while(len(read) == 0):
				print('port open, not responding yet...')
				send_and_leave(mp_inner, 'at')
				read = mp_inner.read(mp_inner.in_waiting)
				print(read)
				time.sleep(1.5)
			port_open = True
			time.sleep(5)
			
		except Exception as e:
			print('could not open port for configuration, retrying...')
			print(e)
			port_open = 0
			time.sleep(2)
			
	return mp_inner
