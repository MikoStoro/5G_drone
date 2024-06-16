import device

config_file = open('./bluetooth.config').readlines()

current_device = None
current_information = None
devices = []
def get_devices():
	for line in config_file:
		line = line.strip().split(" ")
		if line[0] == 'device':
			name = line[1]
			current_device = device.Device(name)
		if line[0] == 'information':
			name = line[1]
			current_information = device.Information(name)
		elif line[0] == 'bytes':
			temp = line[1].split('-')
			current_information.first_byte = int(temp[0])
			current_information.last_byte = int(temp[1])
		elif line[0] == 'bits':
			temp = line[1].split('-')
			current_information.first_bit = int(temp[0])
			current_information.last_bit = int(temp[1])
		elif line[0] == 'scale':
			current_information.scale = float(line[1])
		elif line[0] == 'offset':
			current_information.offset = float(line[1])
		elif line[0] == 'architecture':
			arch = line[1]
			current_information.arch = arch
		elif line[0] == 'end_information':
			current_device.add_information(current_information)
			current_information = None
		elif line[0] == 'end_device':
			devices.append(current_device)
			current_device = None

	return devices
