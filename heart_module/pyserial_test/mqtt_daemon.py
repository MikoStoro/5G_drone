import serial
import time

mp = serial.Serial("/dev/ttyUSB2")

buffer = []

while(True):
    