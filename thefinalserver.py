def server():
    
    import pbagtest171
    import socket
    import os
    
    # Define the target directory
    #target_directory =open("Z://codesWS","w") # Replace with your desired path

    # Ensure the directory exists
    #os.makedirs(target_directory, exist_ok=True)

    # Define the full path for the received file
    file_path = 'received_image.jpg'

    # Set up the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('192.168.0.191', 12346))
    server_socket.listen(1)
    print("Server listening...")

    # Accept a connection
    conn, addr = server_socket.accept()
    print(f"Connected by {addr}")

    feedback=""
    # Receive and save the image
    with open(file_path, "wb") as f:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            f.write(data)

    print(f"Image received and saved to {file_path}")

    # Send a confirmation message
    msg = "Got it"
    feedback+=msg
    feedback+=" "
    #conn.send(msg.encode())
    feedback+=(pbagtest171.testbag("received_image.jpg"))
    #msg = "\nServer here......\n--got the image..."
    #conn.send(msg.encode())
    #while True:
    print(feedback)
    conn.send(feedback.encode())
        
    i=0
    # Close the connection
    try:
        i+=1
        print(i)
        server()
        
    except Exception as e:
        conn.close()
        print("End1",e)

if __name__=="__main__":
    server()
