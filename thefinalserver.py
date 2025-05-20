import socket
import time

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('192.168.55.43', 12346))
server_socket.listen(1)
print("Server listening...")

conn, addr = server_socket.accept()
print(f"Connected by {addr}")

with open("E:\DATASET_Trash_sbh_readwrite_ard\RecievedImage.png", "wb") as f:
    while True:
        data = conn.recv(300000)
        if not data:
            break
        f.write(data)
        
        print("Image received and saved.")

        #print("Image received and saved.")
        IMAGE_PATH = "received_image.jpg"
        print("Image path is : ",IMAGE_PATH)
        #proccess the image now
       # the_prediction=predict_single_image(MODEL_PATH, IMAGE_PATH, (IMAGE_SIZE, IMAGE_SIZE))

        # Evaluate model with dataset
       # evaluate_model(MODEL_PATH, DATA_DIR, BATCH_SIZE, (IMAGE_SIZE, IMAGE_SIZE))
        #conn.sendall(the_prediction)
        t=("happy happy")
        pp="got it"
       

        # Convert to string and send
        message = f"{t}|{pp}"
        conn.sendall(message.encode())
        time.sleep(30)