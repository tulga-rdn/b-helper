import datetime
import json
import asyncio
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message

class IoTDevice:
    def __init__(self, connection_string, datasource, machine_id):
        self.connection_string = connection_string
        self.datasource = datasource
        self.machine_id = machine_id
        self.iot_hub_client = IoTHubDeviceClient.create_from_connection_string(self.connection_string)
        self.total_output_unit_count = 0
        self.machine_speed = 4

    async def connect(self):
        try:
            await self.iot_hub_client.connect()
            print("Connected to Azure IoT Hub.")
        except Exception as e:
            print(f"Failed to connect: {e}")
            raise

    async def send_message(self, message_data, message_type):
        message_json = json.dumps(message_data)
        message = Message(message_json)
        message.content_type = "application/json"
        message.content_encoding = "utf-8"
        message.custom_properties["messageType"] = message_type

        try:
            await self.iot_hub_client.send_message(message)
            print(f"Message sent: {message_data}")
        except Exception as e:
            print(f"Failed to send message: {e}")

    async def send_power_on_event(self):
        event_data = {
            "datasource": self.datasource,
            "equipmentId": self.machine_id,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "totalRunningTime": 0,
            "type": "powerOn",
        }
        await self.send_message(event_data, "MachineEvent")

    async def send_start_running_event(self):
        event_data = {
            "datasource": self.datasource,
            "equipmentId": self.machine_id,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "totalRunningTime": 0,
            "type": "startRunning",
        }
        await self.send_message(event_data, "MachineEvent")

    async def send_telemetry(self):
        """
        Send telemetry data.
        """
        telemetry_data = {
            "telemetry": {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "datasource": self.datasource,
                "machineid": self.machine_id,
                "totaloutputunitcount": self.total_output_unit_count,
                "machinespeed": self.machine_speed,
                "machinestate": 3,  # Producing state
            }
        }
        await self.send_message(telemetry_data, "Telemetry")

    async def run_forever(self):
        await self.send_power_on_event()
        await self.send_start_running_event()

        try:
            while True:
                self.total_output_unit_count += 3

                await self.send_telemetry()

                await asyncio.sleep(10)
        except asyncio.CancelledError:
            print("Run loop cancelled.")
        finally:
            await self.iot_hub_client.disconnect()
            print("Disconnected from Azure IoT Hub.")

# Example usage
async def main():
    CONNECTION_STRING = ""
    DATASOURCE = ""
    MACHINE_ID = ""

    device = IoTDevice(CONNECTION_STRING, DATASOURCE, MACHINE_ID)

    await device.connect()
    await device.run_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted.")