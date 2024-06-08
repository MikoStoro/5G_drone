import modem_utils
import serial
import time
DEVICE = '/dev/ttyUSB2'
CONFIG_PATH = 'config-files/modem.config'

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

mp = open_port()
