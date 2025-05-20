import serial
import time

# Setup serial connection (match COM port and baud rate)
arduino = serial.Serial('COM5', 9600, timeout=1)
time.sleep(2)  # Wait for Arduino to reset

print("Listening to Arduino...")

try:
    while True:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8').strip()
            if line:
                print(f"Arduino says: {line}")

        # Optional: send a test signal
        # arduino.write(b'1')
        # time.sleep(1)

except KeyboardInterrupt:
    print("Stopped listening.")
finally:
    arduino.close()
