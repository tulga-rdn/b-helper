
import lgpio
import time
import asyncio
import datetime
import json
import requests
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message

PWM_PIN = 21
FREQ = 2000
SPEED = 50

IR_SENSOR_PIN = 5
THRESHOLD_DURATION = 3.0

DISCORD_WEBHOOK_URL = ""
def send_discord_message(message):
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
        if response.status_code == 204:
            print("Discord message sent successfully.")
        else:
            print(f"Failed to send Discord message: {response.status_code}")
    except Exception as e:
        print(f"Error while sending Discord message: {e}")

class IoTDevice:
    def __init__(self, connection_string, datasource, machine_id):
        self.connection_string = connection_string
        self.datasource = datasource
        self.machine_id = machine_id
        self.iot_hub_client = IoTHubDeviceClient.create_from_connection_string(self.connection_string)
        self.total_output_unit_count = 0
        self.machine_speed = 4
        self.totalworkingenergy = 0.15

    async def connect(self):
        try:
            await self.iot_hub_client.connect()
            print("Connected to Azure IoT Hub.")
        except Exception as e:
            send_discord_message(f"Failed to connect to Azure IoT Hub: {e}")
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
            send_discord_message(f"Failed to send IoT message: {e}")

    async def send_telemetry(self):
        telemetry_data = {
            "telemetry": {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "datasource": self.datasource,
                "machineid": self.machine_id,
                "totaloutputunitcount": self.total_output_unit_count,
                "machinespeed": SPEED,
                "machinestate": 3,  # Producing state
                "totalworkingenergy": self.totalworkingenergy
            }
        }
        await self.send_message(telemetry_data, "Telemetry")

    async def send_machineevent(self, event_type):
        message = {
            "type": event_type,
            "equipmentId": self.machine_id,
            "jobId": "Lauzhack",
            "totalOutputUnitCount": self.total_output_unit_count,
            "machineSpeed": SPEED,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        }
        await self.send_message(message, "MachineEvent")

# IR Logic (unaltered from test_ir.py)
async def ir_logic(chip, iot_device):
    while True:
        try:
            sensor_value = lgpio.gpio_read(chip, IR_SENSOR_PIN)

            if sensor_value == 0:
                print("Object detected.")
                iot_device.total_output_unit_count += 10

                iot_device.totalworkingenergy += 0.06
                await iot_device.send_telemetry()

                start_time = time.time()
                while lgpio.gpio_read(chip, IR_SENSOR_PIN) == 0:
                    time.sleep(0.1)
                end_time = time.time()

                duration = end_time - start_time

                if duration > THRESHOLD_DURATION:
                    error_message = "Error: Box size exceeds the allowed limit!"
                    print(error_message)
                    send_discord_message(error_message)

            time.sleep(0.1)

        except Exception as e:
            error_message = f"Unexpected error in IR logic: {e}"
            print(error_message)
            send_discord_message(error_message)
            break

def start_motor(chip):
    try:
        lgpio.gpio_claim_output(chip, PWM_PIN)
        lgpio.tx_pwm(chip, PWM_PIN, FREQ, SPEED)
        print("Motor started and running...")
    except Exception as e:
        error_message = f"Error starting motor: {e}"
        print(error_message)
        send_discord_message(error_message)
        raise

def stop_motor(chip):
    try:
        lgpio.tx_pwm(chip, PWM_PIN, FREQ, 0)
        print("Motor stopped.")
    except Exception as e:
        error_message = f"Error stopping motor: {e}"
        print(error_message)
        send_discord_message(error_message)

# Main Program
async def main():
    CONNECTION_STRING = ""
    DATASOURCE = ""
    MACHINE_ID = ""

    device = IoTDevice(CONNECTION_STRING, DATASOURCE, MACHINE_ID)
    await device.connect()
    await device.send_machineevent("powerOn")
    send_discord_message("Machine started, if you have not approved the start, check production line ASAP!")

    chip = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_input(chip, IR_SENSOR_PIN)

    start_motor(chip)
    await device.send_machineevent("startRunning")

    try:
        await ir_logic(chip, device)

    except KeyboardInterrupt:
        send_discord_message("Machine stopped, check production line ASAP!")
        await device.send_machineevent("stopProducing")
        print("\nStopping motor and cleaning up...")
    finally:
        send_discord_message("KeyboardInterrupt")
        stop_motor(chip)
        lgpio.gpiochip_close(chip)
        print("Motor and GPIO cleaned up.")

# Entry point
if __name__ == "__main__":
    asyncio.run(main())
