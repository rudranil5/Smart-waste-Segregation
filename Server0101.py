'''
The module for the smart waste segregation system for the server side.
theControl() is the hub and the main function to handle all other modules and functions.
loadDependencies() loads the databases and models required repeated access all at once
Communication class contains all socket related functions.
writeLog() helps  to maintain the log for errors to be noted
fatalError() is still in development and used to log and close the code in case it is no longer usable

The execution starts from theControll with loading dependencies and establishing socket. currently the dependenceis are global, but could be made
local if required

theControll() creates a directory named Images to store all recieved images in it. then calculates the next photo serial, then it talks to the client
and sends descicion
it first sends the image for detection of multiobject, and then checks for bag and then its class

In case of exception it can log error.
'''

import classificationTest0101
import pbagtest0101 as pbagtest
import contourDetect0101 as contour
import add_rows_mysql as record
import socket
import os
import struct
bagmodel=None
classificationmodel=None
databaseServer=None

def loadDependencies():
    try:
        global bagmodel,classificationmodel,databaseServer
        bagmodel=pbagtest.loadModel()
        print("bagModel Loaded")
        classificationmodel=classificationTest0101.loadModel()
        print("classificationModel loaded")
        databaseServer=record.connectDb()
        writeLog("Dependencies Loaded")
        return 1      #return a list of all loads 
    except Exception as e:
            writeLog(e)
            fatalError(e)
            
def theControl():

    dependencies=loadDependencies() #load models and databases once
    communication=Communication() #object
    communication.connectServer()
    imageDir="Images"
    os.makedirs(imageDir,exist_ok=True)
    count=len(os.listdir(imageDir))+1    #counter for files recieved
    while True: 
        filename=f"image{count}.jpg"   
        file_path=os.path.join(imageDir,filename)

        try: 
            size=communication.recieveSize()
            #print(size) #debug
            imgstate=communication.recieveImg(size,file_path)
            print(f"img {count} received with size-{size}") if not imgstate is None else print("!!!No image recieved")   ###
            #communication.send(f"File {count} recieved... \n")
            #size=communication.recieveSize()
            #moisture=communication.recieve(size)
            #handle broke connection error in vscode
            ifMultiple=contour.processImg(file_path)
            if ifMultiple:
                details=["fromcontour","000"]
                probability=(contour.multiControll(bagmodel,classificationmodel))
                communication.send(probability)
            if not ifMultiple:
                ifBag=(pbagtest.testbag(file_path,bagmodel))#moisture to be added
                details=ifBag.copy()
                if ifBag[-1] == "Recyclable":
                    #return the data
                    communication.send(1)
                elif ifBag[-1] == "Non-Recyclable":
                    communication.send(2)
                    #return the data
                elif ifBag[-1] == 0:     
                    detection=classificationTest0101.predict_single_image(classificationmodel,file_path,(224, 224))
                    print(detection)
                    del details[-1]
                    details.append(detection)
                    communication.send(detection[-1]+1)
                else :
                    #handle no img rec
                    writeLog("Unidentified return from plastic bag detection module")

            record.insertRow(file_path,details[0],details[1])
            print(details)
            writeLog(f"image {count} is saved")
            count+=1
        except KeyboardInterrupt as e:
            communication.closeServer()
            writeLog("Keyboard Interrupt")
            record.closeDb()
            return 1
            
        except Exception as e:
            writeLog(e)
            #communication.closeServer()
            #record.closeDb()


class Communication:
    def connectServer(self,host="0.0.0.0",port=12345):  #establish connection
        # Set up the server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host,port))
        self.server_socket.listen(1)
        print("Server listening...")

        # Accept a connection
        self.conn, self.addr = self.server_socket.accept()
        print(f"Connected by {self.addr}")
        writeLog(f"Connected by {self.addr}")

    def closeServer(self):  #close connection
        print(f"\nClosing connection with {self.addr}")
        writeLog(f"Connection closed with {self.addr}")
        self.conn.close()

    def recieveSize(self):  #recieve the size and unpack as 8 bytes
        try:
            size=b""
            while len(size)<8:
                data=self.conn.recv(8-len(size))
                if not data:
                    break
                size+=data
            return (struct.unpack("!Q",size)[0])
        except Exception as e:
            log= ("Connection Broken ",e)
            writeLog(log)
      
    def recieveImg(self,size,file_path):    #resieve the image as size recieved
        try:
            img=b""
            while len(img)<size:
                data=self.conn.recv(size-len(img))
                if not data:
                    break
                img+=data
            with open(file_path,"wb") as f:
                f.write(img)   
            return 1
        except Exception as e:
            log= ("Connection Broken ",e)
            writeLog(log) 
            return None

    def recieve(self,size):    #recieves messege details of object as string
        try:
            messege=b""
            while len(messege)<size:
                data=self.conn.recv(size-len(messege))
                if not data:
                    break
                messege+=data

            return messege.decode()
        except Exception as e:
            log= ("Connection Broken ",e)
            writeLog(log) 

    def send(self,messege):     #sends the descision as 1 for recyclable, and 2 for non-recyclable
        try:
            self.conn.sendall(struct.pack("!Q",messege))
        except Exception as e:
            log= ("Connection Broken ",e)
            writeLog(log)
    

                
def writeLog(e):    #log to db
    Log=str(e)
    record.writeLogBinServer(Log)

def fatalError(e):  #close all if dependencies not loaded
    print("\nAn error occured-----  \n_____\t_____\n\n",e,"\n\n_____\t_____\n")
    writeLog(e)
    record.closeDb()
    exit()

if __name__=="__main__":
    print("Start")#to debug
    theControl()
