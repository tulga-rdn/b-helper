import lgpio
import time

chip = lgpio.gpiochip_open(0)
IR_SENSOR_PIN = 5
lgpio.gpio_claim_input(chip, IR_SENSOR_PIN)

THRESHOLD_DURATION = 3.0

try:
    while True:
        sensor_value = lgpio.gpio_read(chip, IR_SENSOR_PIN)

        if sensor_value == 0:
            print("Object detected.")
            start_time = time.time()
            while lgpio.gpio_read(chip, IR_SENSOR_PIN) == 0:
                time.sleep(0.1)
            end_time = time.time()
            
            duration = end_time - start_time

            if duration > THRESHOLD_DURATION:
                print("Error: Box size exceeds the allowed limit!")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Program interrupted.")
    lgpio.gpiochip_close(chip)
