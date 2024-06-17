import asyncio
import time
import device
import bt_config_parser as config
import paho.mqtt.client as mqtt
from bleak import BleakScanner

devs = config.get_devices()
names = [ 'iNode-441BE5' ]
timeout = 5
topic = '5gdrone/heart/bluetooth'

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.connect("localhost", 1883, 60)
client.loop_start()


async def discover():
	devices = await BleakScanner.discover(return_adv=True)

	for d in devices.values():
		name = d[1].local_name
		for device in devs:
			if name == device.name:
				adv_data = list(d[1].manufacturer_data.values())[0]
				adv_data = [int(x) for x in adv_data]
				entry = device.get_entry(adv_data)
				print('sending: '  + str(entry))
				client.publish(topic, str(entry))
			
while True:
	asyncio.run(discover())
	time.sleep(timeout)
