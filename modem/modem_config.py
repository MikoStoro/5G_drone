import send_command

DEVICE = '/dev/ttyUSB2'
CONFIG_PATH = 'config-files/modem.config'


file = open(CONFIG_PATH)

commands = file.read().splitlines()
commands = list(filter(lambda x: x != '', commands)) #remove empty lines

for comm in commands:
	print(send_command(comm))
