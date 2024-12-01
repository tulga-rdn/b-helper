# B-Helper

**B-Helper** is a production line monitoring app designed for supervisors. It allows them to track and control production line data efficiently and ensures critical alerts are sent to supervisors, even when they are off-duty. This helps streamline production processes, monitor machine health, and handle rare yet urgent issues without delay.

---

## Features

- **Real-Time Telemetry**: Sends live telemetry data about production, including machine state, speed, and output counts, via Azure IoT Hub.
- **Error Handling and Alerts**:
  - Detects production line errors (e.g., oversized boxes, sensor mismatches) and sends alerts via Discord.
  - Handles unexpected machine stoppages and informs supervisors immediately.
- **Production Control**:
  - Monitors object detection and box sizes using IR and ultrasonic sensors.
  - Controls motor speeds and manages machine start/stop operations programmatically.
- **Hardware Integration**:
  - Utilizes GPIO, PWM, and current sensors (INA219) for physical production line monitoring.
  - Sends detailed telemetry to Azure IoT Hub for further analysis.

---

## Architecture

1. **IoT Communication**: Data is sent to Azure IoT Hub using the `IoTHubDeviceClient` library.
2. **Alerts System**: Alerts are sent via Discord using Webhooks for both telemetry updates and critical errors.
3. **Sensor Systems**:
   - **IR Sensors**: Tracks object detection and logs production output.
   - **Ultrasonic Sensors**: Monitors object proximity to ensure size compliance.
   - **Current Sensors**: INA219-based current monitoring for machine health.

---

## Installation

### Prerequisites

1. Python 3.8+
2. Required libraries:
   - `azure.iot.device`
   - `lgpio`
   - `requests`
   - `adafruit-ina219` (for current sensing)
3. IoT Hub Connection String and Discord Webhook URL.

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/tulga-rdn/b-helper/
   cd b-helper
   ```

2. Install dependencies.

3. Configure your connection settings:
   - Update the `CONNECTION_STRING` and `DISCORD_WEBHOOK_URL` placeholders in `main.py`.

4. Run the application:
   ```bash
   python main.py
   ```

---

## Usage

- **Starting the Application**: Running `main.py` starts the motor and enables the IR and ultrasonic sensors to monitor production.
- **Alerts**:
  - Alerts are sent via Discord when:
    - Machine starts/stops unexpectedly.
    - Errors such as oversized boxes or sensor mismatches are detected.
  - Alerts are configured in `test_discord.py` and `test_error.py`.

---

## Key Modules

1. **`main.py`**: Core logic for telemetry, sensor integration, and IoT Hub communication.
2. **`test_ir.py`**: Handles IR sensor-based object detection.
3. **`test_us.py`**: Manages ultrasonic sensor operations for proximity monitoring.
4. **`test_irus.py`**: Integrates both IR and ultrasonic sensors for comprehensive monitoring.
5. **`test_iot.py`**: Tests IoT Hub communication and telemetry functions.
6. **`test_curr.py`**: Reads current measurements from the INA219 sensor.
7. **`test_bigmotor.py`**: Manages motor control operations for production.

---

## Future Enhancements

- Improved analytics and dashboards via Azure IoT Central.
- Machine learning models for predictive maintenance and anomaly detection.
- Additional notification channels (e.g., SMS or email).

## Contributors

- Tulga-Erdene Sodjargal
- Fakhriyya Mammadova

---
