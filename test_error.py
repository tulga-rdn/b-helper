import lgpio
import time
import requests

PWM_PIN = 21
FREQ = 2000

DISCORD_WEBHOOK_URL = ""
def send_error_to_discord(message):
    payload = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code != 204:
            print(f"Failed to send message to Discord: {response.status_code}")
    except Exception as e:
        print(f"Error sending to Discord: {e}")

def main():
    h = None
    try:
        h = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(h, PWM_PIN)
        lgpio.tx_pwm(h, PWM_PIN, FREQ, 50.0)
        time.sleep(2)

        lgpio.tx_pwm(h, PWM_PIN, FREQ, 20.0)
        time.sleep(5)

        lgpio.tx_pwm(h, PWM_PIN, FREQ, 0)

        send_error_to_discord("Machine stopped unexpectedly. Check production line ASAP")

    except Exception as e:
        print(f"An error occurred: {e}")
        if h is not None:
            lgpio.tx_pwm(h, PWM_PIN, FREQ, 0)
        send_error_to_discord(f"Error: Motor operation interrupted. Details: {e}")

    finally:
        if h is not None:
            lgpio.gpiochip_close(h)
        print("Motor stopped and GPIO cleaned up.")

if __name__ == "__main__":
    tulga = input()
    main()
