import serial
import time

mp = serial.Serial("/dev/ttyUSB2")

try:
	mp.open()
except:
	pass

#mp.write(b'at\r\n')
#print(mp.read(4))
mp.write(b'ati\r\n')
time.sleep(0.1)
waiting = mp.in_waiting
print(waiting)
data = mp.read(waiting)
print(data)
'''print(mp.readline())
print(mp.readline())
print(mp.readline())
print(mp.readline())'''

lines = data.decode().split('\r\n')
print(lines)