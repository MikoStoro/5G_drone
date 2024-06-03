import asyncio
from bleak import BleakScanner
import paho.mqtt.client as mqtt
import time

TARGET_ADDRESS = "D0:F0:18:44:1B:E5"

def bytes_to_hex(data):
    return ' '.join(f'{byte:02X}' for byte in data)

def bytes_to_array(data):
    return [byte for byte in data]

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_disconnect(client, userdata, rc):
    print("Disconnected with result code "+str(rc))

async def monitor():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect("localhost", 1883, 60)
    client.loop_start()

    scanner = BleakScanner()
    while True:
        print("Scanning for devices...")
        devices = await scanner.discover()
        for device in devices:
            if device.address == TARGET_ADDRESS:
                print(f"Target Device Found: {device.name}, Address: {device.address}")

                # Extract and publish advertisement data as an array of bytes
                for key, value in device.metadata.items():
                    if isinstance(value, bytes):
                        array_data = bytes_to_array(value)
                        hex_data = bytes_to_hex(value)
                        print(f"  {key}: {array_data}")
                        client.publish("topic1/subtopic", payload=bytes(array_data))
                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, bytes):
                                array_data = bytes_to_array(sub_value)
                                hex_data = bytes_to_hex(sub_value)
                                print(f"  {key} - {sub_key}: {array_data}")
                                client.publish("topic2/subtopic", payload=bytes(array_data))
                            else:
                                print(f"  {key} - {sub_key}: {sub_value}")
                    else:
                        print(f"  {key}: {value}")
                print("-" * 30)
        await asyncio.sleep(5)  # Scan every 5 seconds

if __name__ == "__main__":
    asyncio.run(monitor())
