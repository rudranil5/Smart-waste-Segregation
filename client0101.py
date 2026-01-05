# client.py
'''This code is prepared for the smart waste segregation system, in case the dustbin to be operated remotely.
It establishes a connection over  the server IP [server code named server0101.py] , and initiates the camera. then it proceeds for the image and data sending to
server and recieving the descicion to put in correct chamber to send to arduino.

it saves a log of all errors (sensor data to be included) in a database.(locally or remotely).

starting with thecontrol() function acting as the main, it has a  class for all functions related to server, and another class related to camera, to ensure secure data availability
across related functions .
user can start  this module after the server is started.

upon disconnection from server midway, the controll module signals arduino to send objects blindly to non recyclable chamber as the Descicive modules are unreachable
and continuously retries to reconnect to server

the loop runs with no conditions for now, except for keyboardinterrupt.
planning ongoing to implement GUI.


0 is the faliure code and 1 the success code

'''
import socket
import cv2
import os
import struct
import add_rows_mysql as record

def writeLog(e):    
    Log=str(e)
    record.writeLogBinClient(Log)   #writes log to an mysql server
    

class ClientConnection: #class containing all socket related modules
    
    def connection(self,host="127.0.0.1",port=12345):   #establish a connection and store it
        print("seeking Server... ")
        client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect((host,port))
        print("Connected")
        self.client=client
        return self.client
    
    def closeConnection(self):      #closes the connection
        print("Disconnected")
        writeLog("Disconnected from server")
        self.client.close()
        
    def sendImg(self,imgPath):  #send image of size specified
        try:
            with open(imgPath,"rb") as f:
                data=f.read(1024)   #the first chunk
                while data:
                    self.client.send(data)
                    data=f.read(1024)
            print("image sent-")
        except Exception as e:
            writeLog(e)
            return 0    
        return 1
    def sendSize(self,size):    #used to send the size to server, required to send items correctly without breaking others
        try:
            self.client.sendall(struct.pack("!Q",size)) #size is packed as 8 bytes always and unpacked as the same too
            print("size sent")
        except ConnectionAbortedError :     #this function alone decides whethe to establish reconnecton
            writeLog("Connection Aborted")
            return 0
        except Exception as e:
            writeLog(e)
            return 0
        
        return 1
    def sendData(self,data):    #send sensor values
        try:
            self.client.sendall(data)
        except Exception as e:
            writeLog(e)
            return 0
        return 1
    def recieve(self):  #recieve descicion fixed size only 1/2
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

def clientSide(full_path,client_socket): #not used
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

class Camera:
    def __init__(self): #Open Camera
        cam = cv2.VideoCapture(0)
        cam.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT,720)

        if not cam.isOpened():
            print("Error: Could not open camera.")
            writeLog("ERROR!!!\n---\nFailed to open Camera\n---\n")
            exit()
        self.cam=cam
        #print("Camera Turned on")
        writeLog("Camera turned on")
    
    #  Shoot Photo 
    def imgCapture(self):

        print("Object detected\t\tCapturing Image...")
        # --- Save path ---
        
        Dir = "Object_at_bin"
        os.makedirs(Dir, exist_ok=True)#improvements needed for multi os or better usage
        filename = "captured_image.jpg"
        full_path = os.path.join(Dir, filename)
        ret, frame = self.cam.read()
        if ret:
            resized_frame = cv2.resize(frame, (512, 512))
            cv2.imwrite(full_path, resized_frame)
            print(f"Saved photo at: {full_path}")  

        self.cam.release()
        cv2.destroyAllWindows()
        return full_path
    
def theControl():   #the hub
    
    Connection=ClientConnection()
    Connection.connection()
    camera=Camera()

    while camera:
        path=camera.imgCapture()
        status=Connection.sendSize(os.path.getsize(path))
        Connection.sendImg(path)
        #get values from arduino, pack in a string= values
        #size of string len(values)=size 
        #Connection.sendSize(size)
        #Connection.sendData(values)
        Descision=Connection.recieve()
        if Descision==1:
            print ("Recyclable")
        elif Descision==2 :
            print("Non-Recyclable")
        else:
            print("Cant get Descicion from server ")
            Descision=2
            writeLog("WARNING!!!\nError Getting Descision from server\n!!!")
        print("Send to chamber : ",Descision,sep=" --------- ",end="\n\n")
        if status==0:
            try:
                Connection.closeConnection()
                print("Disconnected")
                theControl()
            except Exception as e:
                print(e)
                writeLog(e)
                continue
            
        key = cv2.waitKey(1)
        if key % 256 == 27:  # ESC key
            print("Escape hit, closing...")
            Connection.closeConnection()

    Connection.closeConnection()

   
    
if __name__=="__main__":
    record.connectDb()  # establish the db connection seperately
    theControl()
    
