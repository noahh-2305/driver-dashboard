import socket
import time
import json
import numpy as np

# Setup
duration = 60  # seconds
sample_rate = 10  # Hz
total_samples = duration * sample_rate
t = np.linspace(0, duration, total_samples)

# Simulate RPM ramp-up and down
cycle_time = 5  # seconds per cycle
rpm = 600 + (1300 * ((t % cycle_time) / (cycle_time / 2)))
rpm = np.where((t % cycle_time) > (cycle_time / 2),
               1900 - (900 * ((t % cycle_time - (cycle_time / 2)) / (cycle_time / 2))),
               rpm)
rpm = np.clip(rpm, 600, 1900)

# Detect RPM trend (rising/falling)
rpm_diff = np.diff(rpm, prepend=rpm[0])
rpm_rising = rpm_diff > 0.5  # small threshold to ignore flat noise

# Oil pressure: 70 PSI during rise, 30 PSI during fall or idle
oil_pressure = np.where(rpm_rising,
                        np.random.normal(70, 2, total_samples),  # 70 ±2 PSI when accelerating
                        np.random.normal(30, 3, total_samples))  # 30 ±3 PSI when falling/steady

# RPM flag
rpm_flag = (rpm > 1700).astype(int)

# Battery voltage
battery_voltage = 14.3 + 0.1 * np.sin(0.5 * np.pi * t)

# Socket setup
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
address = ('127.0.0.1', 6000)

# Send packets
for i in range(total_samples):
    packet_dict = {
        'RPM': float(round(rpm[i], 2)),
        'OilPress': float(round(oil_pressure[i], 2)),
        'RPM_Above_1700': int(rpm_flag[i]),
        'BatteryVoltage': float(round(battery_voltage[i], 3)),
    }
    message = json.dumps(packet_dict).encode()
    print(f"Sending {packet_dict}")
    sock.sendto(message, address)
    time.sleep(1 / sample_rate)