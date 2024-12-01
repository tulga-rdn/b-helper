import lgpio
import time

PWM_PIN = 21
FREQ = 2000

def main():
    try:
        h = lgpio.gpiochip_open(0)

        lgpio.gpio_claim_output(h, PWM_PIN)

        print("Starting motor at 50% power...")
        lgpio.tx_pwm(h, PWM_PIN, FREQ, 50.0)

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping motor...")
    finally:
        lgpio.tx_pwm(h, PWM_PIN, FREQ, 0)
        lgpio.gpiochip_close(h)
        print("Motor stopped and GPIO cleaned up.")

if __name__ == "__main__":
    main()
