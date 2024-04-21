import asyncio
from bleak import BleakScanner

DEVICE_ADDRESS = "D0:F0:18:44:1B:E5"

async def read_device_data():
    scanner = BleakScanner()

    async def callback(device, advertisement_data):
        if device.address == DEVICE_ADDRESS:
            print(f"Device found: {device.address} - {device.name}")
            print("Advertisement data:", advertisement_data)
            if "manufacturer_data" in advertisement_data:
                manufacturer_data = advertisement_data["manufacturer_data"]
                print("Manufacturer data:", manufacturer_data.hex())  # Convert bytes to hex for easy viewing

    scanner.register_detection_callback(callback)
    await scanner.start()

    while True:
        await asyncio.sleep(10)  # Scanning for 10 seconds

asyncio.run(read_device_data())
