import asyncio
import os
import platform
import paho.mqtt.client as mqtt
from bleak import BleakScanner, BleakClient

TARGET_DEVICE_ADDRESS = "D0:F0:18:44:1B:E5"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "ble/device/data"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))

def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT broker with result code " + str(rc))

async def list_services_and_characteristics(device, mqtt_client):
    try:
        async with BleakClient(device.address, timeout=30.0) as client:
            if not await client.is_connected():
                await client.connect()
                
            print(f"Connected to {device.name} ({device.address})")
            services = await client.get_services()
            
            device_info = {"name": device.name, "address": device.address, "characteristics": {}}
            
            for service in services:
                for characteristic in service.characteristics:
                    value = None
                    for attempt in range(3):  # Retry up to 3 times
                        try:
                            if 'read' in characteristic.properties:
                                await asyncio.sleep(1)  # Add a delay between reads
                                value = await client.read_gatt_char(characteristic)
                                value = value.decode('utf-8', errors='ignore')
                                break
                        except Exception as e:
                            print(f"  Attempt {attempt+1} failed for characteristic {characteristic.uuid}: {e}")
                    
                    if value is not None:
                        device_info["characteristics"][characteristic.uuid] = value
            
            # Remove entries with empty values from the characteristics dictionary
            device_info["characteristics"] = {k: v for k, v in device_info["characteristics"].items() if v}
            
            print(f"Device info for {device.name} ({device.address}): {device_info}")
            
            # Convert the dictionary to a string
            payload = str(device_info)
            mqtt_client.publish(MQTT_TOPIC, payload=payload)
            print(f"Data sent to MQTT topic {MQTT_TOPIC}")
            
    except Exception as e:
        print(f"Could not connect to device {device.name} ({device.address}): {e}")

async def scan_and_list_devices(mqtt_client):
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()

    if not devices:
        print("No devices found.")
        return

    target_device = next((device for device in devices if device.address == TARGET_DEVICE_ADDRESS), None)

    if not target_device:
        print(f"Target device {TARGET_DEVICE_ADDRESS} not found.")
        return

    print(f"Found target device: {target_device.name} ({target_device.address})")
    
    print(f"Connecting to target device {target_device.name} ({target_device.address})...")
    await list_services_and_characteristics(target_device, mqtt_client)

def turn_bluetooth_off_on():
    os_name = platform.system()
    if os_name == "Windows":
        os.system("powershell -Command \"Get-Service bthserv | Stop-Service\"")
        os.system("powershell -Command \"Get-Service bthserv | Start-Service\"")
    elif os_name == "Linux":
        os.system("sudo systemctl stop bluetooth")
        os.system("sudo systemctl start bluetooth")
    else:
        print(f"Bluetooth control not supported on {os_name}")

async def main():
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

    while True:
        await scan_and_list_devices(mqtt_client)
        print("Turning Bluetooth off and on...")
        turn_bluetooth_off_on()
        print("Waiting for the next scan...")
        await asyncio.sleep(30)  # Wait 30 seconds before the next scan

# Run the main function
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
