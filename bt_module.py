from time import sleep
import bleson 
from bleparser import BleParser
import paho.mqtt.client as mqtt



#main function
def on_advertisement(advertisement):
   data = advertisement.mfg_data
   if data is not None:
	   name = {"name" : advertisement.name}
	   #data = bytes(bytearray.fromhex(str(data)))
	   print(bytearray(data))
	   sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)
	   
	   if sensor_msg is None and tracker_msg is None:
		   return 
	   
	   result = {}
	   try: result = result | name
	   except:pass
	   
	   try: result = result | sensor_msg
	   except:pass
	   
	   try:result = result | tracker_msg
	   except: pass
	   
	   result = str(result)
	   print("sending: " + result)
	   
	   client.publish(bluetooth_topic, str(result))
	   



#Bleson setup
# Bleson is responsible for gathering data
adapter = bleson.get_provider().get_adapter()
observer = bleson.Observer(adapter)
observer.on_advertising_data = on_advertisement

#BLE parser setup
#this object is resposnible for parsing data gathered by Bleson Observer
ble_parser = BleParser(report_unknown=True)

#mqtt callbacks
def on_connect(client, userdata, flags,rc, arg):
    print("Connected to MQTT broker with result code " + str(rc))

def on_disconnect(client, userdata, rc, arg):
    print("Disconnected from MQTT broker with result code " + str(rc))

#mqtt client setup
#client resposnible for sending gathered data to heart
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "ble/device/data"
bluetooth_topic = '5gdrone/heart/bluetooth'

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

while True:
	observer.start()
	sleep(10)
	observer.stop()
	sleep(30)
