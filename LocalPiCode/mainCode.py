from time import sleep
import socket
import time
import os
import shutil
import subprocess
import random
import serial
import serial.tools.list_ports
import csv
import threading
from threading import Thread

class COMMAND:
## Command sending ##
    def __init__(self):
        self.buffSize = 2048
        self.ServerPort = 2244
        self.ServerIP = '172.20.10.7'


        self.ser = serial.Serial('/dev/ttyACM0',9600, timeout = 1.0, xonxoff = True)
        self.ser.close()
        self.ser.open()
        self.ser.reset_input_buffer()
        self.PSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #using UDP
        self.PSock.bind((self.ServerIP,self.ServerPort))

        self.func2c = threading.Thread(target=self.comloop, daemon=True)
        self.func2c.start()
        self.func2c.join()


    def comloop(self):
        while not False:
            message, address = self.PSock.recvfrom(self.buffSize) # waiting until Pi connects with client
            message = message.decode('utf-8')           

            if self.ser.in_waiting > 0: # returns the number of bytes recieved
                time.sleep(0.01)
                if(self.ser.in_waiting > self.buffSize):
                    self.ser.reset_input_buffer()
                else:
                    self.ser.reset_input_buffer()
                    self.ser.write((message + '\n').encode('utf-8'))



## Sensor Data Interpretation

class dataInterchange:
    def __init__(self):
        self.buffSize = 2048
        self.ServerPort = 2224
        self.ServerIP = '172.20.10.7'
        self.line = '1'

        self.func2 = threading.Thread(target=self.senDat, daemon=True)
        self.func2.start()
        self.func2.join()


    def senDat(self):
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout = 1.0) #
        ser.setDTR(False)
        ser.flushInput()
        ser.setDTR(True)
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        print("Serial is working!")

        self.bytesSending = self.line.encode('utf-8')
        self.PSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #using UDP
        self.PSock.bind((self.ServerIP,self.ServerPort))
        print('Server is up and listening...')
        self.message, self.address = self.PSock.recvfrom(self.buffSize) # waiting until Pi connects with client
        self.message = self.message.decode('utf-8')
        
        self.counter = 0
        
        while not False:
            # Receiving data
            if ser.in_waiting > 0: # returns the number of bytes received
                time.sleep(0.01)
                if(ser.out_waiting > self.buffSize):
                    print('BUFFER OVERFLOW')
                    ser.reset_output_buffer()
                    # ser.reset_input_buffer()
                else:
                    try:
                        ser.reset_output_buffer()
                        self.line = ser.readline().decode('utf-8').rstrip()
                    except:
                        pass
                    print(self.line)
                    self.bytesSending = self.line.encode('utf-8')
                    self.PSock.sendto(self.bytesSending,self.address)
                    self.counter += 1


# Run commands to be threaded
commandThread = threading.Thread(target=COMMAND, daemon=True)
dataThread =  threading.Thread(target=dataInterchange, daemon=True)

commandThread.start()
dataThread.start()

commandThread.join()
dataThread.join()


