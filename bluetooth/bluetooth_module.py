import asyncio
import time

from bleak import BleakScanner


names = [ 'iNode-441BE5' ]
offset = -2
async def discover():
	devices = await BleakScanner.discover(return_adv=True)

	for d in devices.values():
		name = d[1].local_name
		if name not in names:
			continue
		try:
			adv_data = list(d[1].manufacturer_data.values())[0]
			print(adv_data)
			print(type(adv_data))
			print(adv_data.hex())
			#adv_data = str(adv_data)
			adv_data = [int(x) for x in adv_data]
			print(adv_data[8], adv_data[1])
			print(adv_data[9]+adv_data[8])
			#tmp = (175.72 * int(adv_data[9] + adv_data[8],16) * 4 / 65536) - 46.85
			tmp = (175.72 * (adv_data[9+offset]*256 + adv_data[8+offset]) * 4 / 65536) - 46.85
			hum = (125 * (adv_data[11+offset]*256 + adv_data[10+offset]) * 4 / 65536) - 6
			
			t1 = (adv_data[13+offset]*256 + adv_data[12+offset]) << 16
			t2 = (adv_data[15+offset]*256 + adv_data[14+offset])
			t = t1 | t2
			to = time.gmtime(t)
			print('TEMPERATURE: ' + str(tmp))
			print('HUMIDITY: ' + str(hum))
			print('TIME: ' + str(to))
		except Exception as e:
			print(e)
		#sensor_msg, tracker_msg = ble_parser.parse_raw_data(adv_data)
		#print(sensor_msg,tracker_msg)
			
 
			

asyncio.run(discover())
