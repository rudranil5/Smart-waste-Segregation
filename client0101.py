# client.py
'''The init will call the img capture module by default, and reffered to the client

or else init can also call client , and client can refer to imgcapture first then
execute itself, that would require certain change
'''
import socket
import cv2
import os
import struct

def writeLog(e):
    print("Error occured - ",e)

class connection:
    
    def connection(self,host="127.0.0.1",port=12345):
        print("seeking Server... ")
        client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect((host,port))
        print("Connected")
        self.client=client
        return self.client
    
    def sendImg(self,imgPath):
        try:
            with open(imgPath,"rb") as f:
                data=f.read(1024)
                while data:
                    self.client.send(data)
                    data=f.read(1024)
            print("image sent-")
        except Exception as e:
            writeLog(e)
        return
    def sendSize(self,size):
        try:
            self.client.sendall(struct.pack("!Q",size))
            print("size sent")
        except Exception as e:
            writeLog(e)
        
    def sendData(self,data):
        try:
            self.client.sendall(data)
        except Exception as e:
            writeLog(e)
        return
    def recieve(self):
        feedback=None
        try:
            data=b""
            while len(data)<8:
                data+=self.client.recv(8-len(data))
                if not data:
                    return feedback
            feedback=(struct.unpack("!Q",data)[0])
            print("recieved descision")
        except Exception as e:
            writeLog(e)
        return feedback

def clientSide(full_path,client_socket):
    import struct
    import os
    file_size = os.path.getsize(full_path)
    client_socket.sendall(struct.pack("!Q",file_size))
    # --- Send the image file ---
    with open(full_path, "rb") as f:
        data = f.read(1024)
        while data:
            client_socket.send(data)
            data = f.read(1024)
            
    print("Image sent successfully.")

    # --- Shutdown write & wait for server response ---
    #client_socket.shutdown(socket.SHUT_WR)

    data=client_socket.recv(1).decode()
    print(data)
    client_socket.close()

#  Open camera & shoot Photo 
def imgCapture():

    print("Object detected\t\tCapturing Image...")
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT,720)

    if not cam.isOpened():
        print("Error: Could not open camera.")
        exit()

    # --- Save path ---
    Dir = r"C:\Desktop"
    filename = "captured_image.jpg"
    full_path = os.path.join(Dir, filename)
    os.makedirs(Dir, exist_ok=True)
    ret, frame = cam.read()
    if ret:
        resized_frame = cv2.resize(frame, (512, 512))
        cv2.imwrite(full_path, resized_frame)
        print(f"Saved photo at: {full_path}")  

    cam.release()
    cv2.destroyAllWindows()
    return full_path

if __name__=="__main__":
    Connection=connection()
    Connection.connection()
    while connection:
        path=imgCapture()
        Connection.sendSize(os.path.getsize(path))
        Connection.sendImg(path)
        Descision=Connection.recieve()
        if Descision==1:
            print (f"Recyclable{Descision}")
        else :
            print(f"Non-Recyclable{Descision}")
        print("Send to chamber : ",Descision,sep=" --------- ",end="\n\n")
        key = cv2.waitKey(1)
        if key % 256 == 27:  # ESC key
            print("Escape hit, closing...")
            connection.close()
    connection.close()
