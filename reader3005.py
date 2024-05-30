import asyncio
from bleak import BleakScanner, BleakClient

async def list_services_and_characteristics(device):
    try:
        async with BleakClient(device) as client:
            services = await client.get_services()
            print(f"Services for device {device.name} ({device.address}):")
            for service in services:
                print(f"- {service.uuid}: {service.description}")
                for characteristic in service.characteristics:
                    value = None
                    try:
                        if 'read' in characteristic.properties:
                            value = await client.read_gatt_char(characteristic.uuid)
                            value = value.decode('utf-8', errors='ignore')
                    except Exception as e:
                        print(f"  Could not read characteristic {characteristic.uuid}: {e}")
                    print(f"  Characteristic {characteristic.uuid}: {characteristic.description}, Value: {value}")
    except Exception as e:
        print(f"Could not connect to device {device.name} ({device.address}): {e}")

async def main():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()

    if not devices:
        print("No devices found.")
        return

    print(f"Found {len(devices)} devices:")
    for i, device in enumerate(devices):
        print(f"{i}: {device.name} ({device.address})")

    # Connect to each device found
    for device in devices:
        print(f"Connecting to device {device.name} ({device.address})...")
        await list_services_and_characteristics(device)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
