#!/usr/bin/env python3
import test
import cv2
import time

# Open the laptop camera (device 0)
cap = cv2.VideoCapture(0)
i=1
while i<=5:
    if not cap.isOpened():
        print("Cannot access camera")
        exit()
    print("Get ready")
    time.sleep(3)
    ret, frame = cap.read()

    if ret:
        i+=1
        k=(f"photo{i}.jpg")
        
        cv2.imwrite(k, frame)
        print(f"Photo saved as photo{k}.jpg")
        time.sleep(10)
    else:
        print("Failed to capture image")

cap.release()
test.predict_single_image(model_path, f"photo{k}.jpg", 500)
