import lgpio
import time
import requests

IR_SENSOR_PIN = 5
TRIG_PIN = 26
ECHO_PIN = 6

THRESHOLD_DURATION = 3.0
MAX_DISTANCE_CM = 100
SPEED_OF_SOUND_CM_S = 34300
MAX_DURATION = (MAX_DISTANCE_CM * 2) / SPEED_OF_SOUND_CM_S
US_DEBOUNCE_TIME = 3

WEBHOOK_URL = ""
ir_count = 0
us_count = 0
us_object_present = False  
us_last_detected_time = 0  

chip = lgpio.gpiochip_open(0)
lgpio.gpio_claim_input(chip, IR_SENSOR_PIN)
lgpio.gpio_claim_output(chip, TRIG_PIN)
lgpio.gpio_claim_input(chip, ECHO_PIN)

def get_distance():
    lgpio.gpio_write(chip, TRIG_PIN, 1)
    time.sleep(0.00001)
    lgpio.gpio_write(chip, TRIG_PIN, 0)

    pulse_start = time.time()
    start_timeout = pulse_start
    while lgpio.gpio_read(chip, ECHO_PIN) == 0:
        pulse_start = time.time()
        if pulse_start - start_timeout > MAX_DURATION:
            return 999999

    pulse_end = time.time()
    while lgpio.gpio_read(chip, ECHO_PIN) == 1:
        pulse_end = time.time()
        if pulse_end - pulse_start > MAX_DURATION:
            return 999999

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * SPEED_OF_SOUND_CM_S / 2
    return distance

def send_to_discord(message):
    payload = {"content": message}
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code != 204:
            print(f"Failed to send message to Discord: {response.status_code}")
    except Exception as e:
        print(f"Error sending to Discord: {e}")

try:
    while True:
        ir_value = lgpio.gpio_read(chip, IR_SENSOR_PIN)
        if ir_value == 0:
            print("IR Sensor: Object detected.")
            ir_count += 1

            start_time = time.time()
            while lgpio.gpio_read(chip, IR_SENSOR_PIN) == 0:
                time.sleep(0.1)
            duration = time.time() - start_time

            if duration > THRESHOLD_DURATION:
                error_message = "A box with larger size just passed the production line!"
                send_to_discord(error_message)

        distance = get_distance()
        current_time = time.time()

        if distance < 6:
            if not us_object_present:
                if current_time - us_last_detected_time > US_DEBOUNCE_TIME:
                    print("Ultrasonic Sensor: Object detected.")
                    us_count += 1
                    us_object_present = True
                    us_last_detected_time = current_time

            start_time = time.time()
            while get_distance() < 6:
                time.sleep(0.1)
            duration = time.time() - start_time

            if duration > THRESHOLD_DURATION:
                error_message = "A box with larger size just passed the production line!"
                send_to_discord(error_message)

        else:
            if current_time - us_last_detected_time > US_DEBOUNCE_TIME:
                us_object_present = False
        if abs(ir_count - us_count) > 1:
            error_message = f"Error: Sensor counts mismatch! Check the production line ASAP"
            send_to_discord(error_message)
            ir_count = 0
            us_count = 0

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nProgram interrupted.")
finally:
    lgpio.gpiochip_close(chip)
    print("GPIO cleaned up.")
