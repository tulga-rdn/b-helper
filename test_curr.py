import board
import busio
from adafruit_ina219 import INA219

i2c_bus = busio.I2C(board.SCL, board.SDA)

ina219 = INA219(i2c_bus)

def read_current():
    try:
        current_ma = ina219.current
        print(f"Current: {current_ma:.2f} mA")
    except Exception as e:
        print(f"Error reading current: {e}")

if __name__ == "__main__":
    print("Reading current from INA219 sensor...")
    while True:
        read_current()
