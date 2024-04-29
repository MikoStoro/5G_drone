import serial
import time
import send_command as comm



mp = serial.Serial("/dev/ttyUSB2")

buffer = []

while(True):
    
    time.sleep(0.1)