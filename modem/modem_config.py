import modem_utils
import serial
import time
DEVICE = '/dev/ttyUSB2'
CONFIG_PATH = 'config-files/modem.config'


file = open(CONFIG_PATH)

commands = file.read().splitlines()
commands = list(filter(lambda x: x != '', commands)) #remove empty lines

all_sent = False

mp = modem_utils.open_port()





while not all_sent:
	try:
		for comm in commands:
			if comm[0] != '#':
				modem_utils.send_and_leave(mp, comm)
				print(modem_utils.read_response(mp))
		all_sent = True
		print('sent all commands!')
	except Exception as e: 
		print("Cannot send commands, retrying...")
		print(e)
		mp = open_port()
		time.sleep(1)
