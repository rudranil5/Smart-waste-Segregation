
'''
    
    import serial
    import time
    # Send to Arduino
    try:
        arduino = serial.Serial('COM5', 9600, timeout=1)
        time.sleep(2)  # Let Arduino initialize
        arduino.write(str(label).encode())
        print(f"Sent to Arduino: {label}")
        
        while True:
            if arduino.in_waiting > 0:
                line = arduino.readline().decode('utf-8').strip()
                if line:
                    print(f"Arduino : {line}")

        # Optional: send a test signal
        # arduino.write(b'1')
        # time.sleep(1)

    except KeyboardInterrupt:
        print("Stopped listening.")
    finally:
        arduino.close()
   # except serial.SerialException as e:
    #    print(f"Failed to send to Arduino: {e}")
'''