

class Information:
	def __init__(self, name = None):
		self.name = name
		self.first_byte = None
		self.last_byte = None
		self.first_bit = None
		self.last_bit = None
		self.scale = None
		self.offset = None
		self.arch = 'LE'
	
	def get_bytes(self, adv_data):
		print(self.name)
		result = 0
		last = self.last_byte
		first = self.first_byte
		bytes_count = self.last_byte - self.first_byte + 1
		weight = 1
		if self.arch == 'BE':
			for i in range(bytes_count):
				result += adv_data[last-i] * weight
				weight *= 256
		else:
			for i in range(bytes_count):
				result += adv_data[first+i] * weight
				weight *= 256
		return result
		
	def get_bits(self, value):
		bits_count = self.last_bit - self.first_bit +1
		mask = (2**bits_count) -1
		return (value >> (self.first_bit - 1)) & mask
	
	def calculate(self, adv_data):
		value = self.get_bytes(adv_data)
				
		if self.first_bit is not None and self.last_bit is not None:
			value = self.get_bits(value)
		if self.scale is not None:
			value *= self.scale
		if self.offset is not None:
			value += self.offset
		
		return value
		
		

class Device:
	def __init__(self, name = None):
		self.name = name
		self.informations = []
		
	def add_information(self,information:Information):
		self.informations.append(information)
	
	def get_entry(self, adv_data):
		entry = {}
		for info in self.informations:
			entry[info.name] = info.calculate(adv_data)
		return entry
	
	def __str__(self):
		return self.name
	
	
