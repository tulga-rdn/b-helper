import lgpio
import time

TRIG_PIN = 26
ECHO_PIN = 6

# <3cm = box present

MAX_DISTANCE_CM = 100
SPEED_OF_SOUND_CM_S = 34300
MAX_DURATION = (MAX_DISTANCE_CM * 2) / SPEED_OF_SOUND_CM_S

def setup():
    h = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_output(h, TRIG_PIN)
    lgpio.gpio_claim_input(h, ECHO_PIN)
    return h

def get_distance(h):
    lgpio.gpio_write(h, TRIG_PIN, 1)
    time.sleep(0.00001)
    lgpio.gpio_write(h, TRIG_PIN, 0)

    pulse_start = time.time()
    start_timeout = pulse_start
    while lgpio.gpio_read(h, ECHO_PIN) == 0:
        pulse_start = time.time()
        if pulse_start - start_timeout > MAX_DURATION:
            return 999999

    pulse_end = time.time()
    while lgpio.gpio_read(h, ECHO_PIN) == 1:
        pulse_end = time.time()
        if pulse_end - pulse_start > MAX_DURATION:
            return 999999

    pulse_duration = pulse_end - pulse_start

    distance = pulse_duration * SPEED_OF_SOUND_CM_S / 2
    return distance, pulse_duration

def cleanup(h):
    lgpio.gpiochip_close(h)

if __name__ == "__main__":
    try:
        gpio_handle = setup()

        while True:
            distance, duration = get_distance(gpio_handle)
            if distance < 6:
                print("Object detected.")
            time.sleep(1) 
    except KeyboardInterrupt:
        print("\nMeasurement stopped by user.")
    finally:
        cleanup(gpio_handle)
        print("GPIO cleaned up.")
