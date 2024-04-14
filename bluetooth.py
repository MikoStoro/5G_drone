import bluetooth._bluetooth as bluez
import paho.mqtt.client as mqtt
import threading
import time

# MQTT Callbacks
flag_connected = 0

def on_connect(client, userdata, flags, rc):
   global flag_connected
   flag_connected = 1
   print("Connected with result code "+str(rc))

def on_disconnect(client, userdata, rc):
   global flag_connected
   flag_connected = 0
   print("Disconnected with result code "+str(rc))

# HCI Dump Function
def hci_dump():
    # Open the first available Bluetooth adapter
    sock = bluez.hci_open_dev(0)
    
    # Set the HCI filter to capture all incoming and outgoing packets
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_all_ptypes(flt)
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)
    
    # Begin capturing HCI packets
    while True:
        pkt = sock.recv(1024)
        # Check if the packet starts with the specified bytes
        if pkt.startswith(b'\x04\x3E\x29\x02'):
            decimal_representation = int.from_bytes(pkt, byteorder='big')
            decimal_string = ' '.join(str(byte) for byte in pkt)
            print(decimal_string)
            client.publish("topic2/subtopic", pkt)

# MQTT Client Configuration
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.connect("localhost", 1883, 60)
client.loop_start()

# Main Loop
while True:
    # Start HCI dump thread
    hci_thread = threading.Thread(target=hci_dump)
    hci_thread.start()
    
    # Check MQTT connection status
    if flag_connected == 1:
        # Publish message
        client.publish("topic2/subtopic", "1")
        time.sleep(1)
        client.publish("topic1/subtopic", "0")
        time.sleep(1)
    else:
        # Wait to reconnect
        time.sleep(5)
        client.reconnect()

    # Wait for HCI thread to finish before starting another instance
    hci_thread.join()
