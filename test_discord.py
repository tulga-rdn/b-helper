import requests
import datetime
import time

DISCORD_WEBHOOK_URL = ""
def send_discord_message(content):
    data = {"content": content}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        response.raise_for_status()
        print(f"Message sent: {content}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message: {e}")

def run_forever():
    try:
        # Send a startup message
        send_discord_message("Machine is powered on and started running.")

        total_output_count = 0
        machine_speed = 4

        while True:
            timestamp = datetime.datetime.utcnow().isoformat() + "Z"
            total_output_count += 3
            message = (
                f"**Telemetry Update**\n"
                f"Timestamp: {timestamp}\n"
                f"Machine Speed: {machine_speed}\n"
                f"Total Output Count: {total_output_count}\n"
                f"Machine State: Producing"
            )
            send_discord_message(message)
            time.sleep(10)
    except KeyboardInterrupt:
        send_discord_message("Machine has been powered off.")
        print("Program stopped by user.")

if __name__ == "__main__":
    run_forever()
