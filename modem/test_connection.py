print('xd')
import modem_utils as modem
import serial
import time
DEVICE = '/dev/ttyUSB2'
CONFIG_PATH = 'config-files/modem.config'

mp = modem.open_port(DEVICE)

 

while(True):
	print(modem.send_and_wait(mp, 'at'))
	
	time.sleep(1)
