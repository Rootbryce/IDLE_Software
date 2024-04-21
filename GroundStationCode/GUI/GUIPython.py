# This will be the code for the live data visualisation and GUI that has all the buttons!
# Using: Tkinter
# Root: the base GUI box/platform thing that everything shows up on
# Frame: basically just sub-roots that can have data visuallisation or other similar things on them
# Wigets: Buttons and stuff like that seen on the frames
import threading
import time
import csv
import socket
from tkinter import *
from tkinter import ttk
from faker import Faker
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from itertools import count
#from tkmacosx import Button
import pandas as pd

# Initializing variables for timer
pause = True 
startNow = time.time()
ElapsedTime = 0
timerup = 900

# "Locking" Dig Mode
digLock = True #Dig Mode "Locked"


class RootGUI:
    def __init__(self):
        self.root = Tk()  # initialising root
        self.root.title("IDLE GUI Bruh")
        self.root.geometry("1440x820")
        self.root.resizable(True,True)
        self.root.config(bg="black")

# Building Frame:


class BUTTONS():
    def __init__(self, root, buffer, UDPClient, serverAddress):
        self.root = root
        self.buffer = buffer
        self.UDPClient = UDPClient
        self.serverAddress = serverAddress
        self.commanddig = 'Dig Pressed!'
        self.commanddig = self.commanddig.encode('utf-8')
        self.commandsafe = 'Safe Pressed!'
        self.commandsafe = self.commandsafe.encode('utf-8')
        self.commandstop = 'Stop Pressed!'
        self.commandstop = self.commandstop.encode('utf-8')
        self.commandsleep = 'Sleep Pressed!'
        self.commandsleep = self.commandsleep.encode('utf-8')
        self.frame = LabelFrame(root, text="Mode Commands", padx=25, pady=25, fg = "white", bg="black")
        self.DIG = Button(self.frame, text="DIG", bg="grey", width=15, command=self.digcheck)
        self.SAFE = Button(self.frame, text="SAFE", bg="grey", width=15, command=self.safecheck)
        self.SLEEP = Button(self.frame, text="SLEEP", bg="red", width=15, command=self.sleepcheck)
        self.STOP = Button(self.frame, text="STOP", bg="grey", width=15, command=self.stopcheck)

        self.publish2()

    def digcheck(self):

        self.DIG.configure(bg = "red")
        self.SAFE.configure(bg = "grey")
        self.SLEEP.configure(bg = "grey")
        self.STOP.configure(bg = "grey")
        print("Dig Pressed")
        self.commanddig = "Dig Mode"
        self.commanddig = self.commanddig.encode('utf-8')
        self.UDPClient.sendto(self.commanddig, self.serverAddress)

        global pause
        global startNow
        global ElapsedTime
        global digLock
        digLock = False
         

        if ElapsedTime >= timerup:  # If 1 cycle is already completed, this will restart Dig Mode
            ElapsedTime = 0
  

    def safecheck(self):
        self.DIG.configure(bg = "grey")
        self.SAFE.configure(bg = "red")
        self.SLEEP.configure(bg = "grey")
        self.STOP.configure(bg = "grey")
        print("Safe Pressed")
        self.commandsafe = "Safe Mode"
        self.commandsafe = self.commandsafe.encode('utf-8')
        self.UDPClient.sendto(self.commandsafe, self.serverAddress)

        global digLock
        global pause

        digLock = True

        # Pause timer
        if pause == False: 
            pause = True
            if ElapsedTime < timerup:
                UpdateElapsedTime()     

    def sleepcheck(self):
        self.DIG.configure(bg = "grey")
        self.SAFE.configure(bg = "grey")
        self.SLEEP.configure(bg = "red")
        self.STOP.configure(bg = "grey")
        print("Sleep Pressed")
        self.commandsleep = "Sleep Mode"
        self.commandsleep = self.commandsleep.encode('utf-8')
        self.UDPClient.sendto(self.commandsleep, self.serverAddress)

        global digLock
        global pause

        digLock = True

        # Pause timer
        if pause == False: 
            pause = True
            if ElapsedTime < timerup:
                UpdateElapsedTime() 

        # # Stop Drum
        # delay_converted = 500
        # delay_converted = str(delay_converted) 
        # print("delay_converted = " + delay_converted)
        # self.delay_converted = delay_converted.encode('utf-8')
        # self.UDPClient.sendto(self.delay_converted, self.serverAddress)

        # # Raise Linear Actuator
        # self.commandLinearActuator = 'UP'
        # print(self.commandLinearActuator)
        # self.commandLinearActuator = self.commandLinearActuator.encode('utf-8')
        # self.UDPClient.sendto(self.commandLinearActuator, self.serverAddress)



    def stopcheck(self):
        self.DIG.configure(bg = "grey")
        self.SAFE.configure(bg = "grey")
        self.SLEEP.configure(bg = "grey")
        self.STOP.configure(bg = "red")
        print("Stop Pressed")
        self.commandstop = "Stop Mode"
        self.commandstop = self.commandstop.encode('utf-8')
        self.UDPClient.sendto(self.commandstop, self.serverAddress)

        global digLock
        global pause

        digLock = True

        if pause == False: 
            pause = True
            if ElapsedTime < timerup:
                UpdateElapsedTime()    

        delay_converted = 500

        delay_converted = str(delay_converted) 
        print("delay_converted = " + delay_converted)
        self.delay_converted = delay_converted.encode('utf-8')
        self.UDPClient.sendto(self.delay_converted, self.serverAddress)
    

    def publish2(self):
        self.frame.grid(row=0, column=0)
        self.DIG.grid(column=1, row=1)
        self.SAFE.grid(column=2, row=1)
        self.SLEEP.grid(column=3, row=1)
        self.STOP.grid(column=4, row=1)


class RUNNING_TIMER():  
    
    def __init__(self, root, UDPClient, serverAddress): 
        self.start_time = time.time()
        self.root = root
        self.UDPClient = UDPClient
        self.serverAddress = serverAddress
        self.frame4 = LabelFrame(root, text="Live Time", padx=25, pady=25, fg= "white", bg="black")
        self.frame10 = Button(root,text = "Start Timer", padx=25, pady=25, fg= "black", bg="grey", command=self.starttimer)
        self.time_passed = Label(root, text="", font=("Helvectica", 37), fg= "white", bg="black")
        self.threading = FALSE


        self.updatetime()
        self.publish3()


    def starttimer(self):
        if digLock == False:
            global pause
            global startNow

            if pause == True:
                pause = False
                startNow = time.time()
                UpdateElapsedTime()
            
            else:
                pause = True
                if ElapsedTime < timerup:
                    UpdateElapsedTime()        
                elif ElapsedTime >= timerup:
                    pass

        else:
            pass


    def updatetime(self):

        global pause
        global ElapsedTime
        self.start_time2 = time.time()
        self.current_time = int(self.start_time2 - startNow + ElapsedTime)
        sec = ""
        if self.current_time < timerup:
            min = int(self.current_time/60)
            sec_entire = self.current_time
            minsec = sec_entire/60
            minsecmin = int(minsec)
            sec = int((minsec - minsecmin)*60)
        elif self.current_time == timerup:
            pause = True
            UpdateElapsedTime()
        elif self.current_time > timerup:
            min = int(timerup/60)
            sec = int(0)
            
     

        if pause == False:
            self.time_passed.config(text = "{m:02d} : {s:02d}".format(m=min,s=sec), fg = "white", bg = "black")
            self.time_passed.after(100, self.updatetime)
        elif pause == True:
            min = int(ElapsedTime/60)
            sec_entire = ElapsedTime
            minsec = sec_entire/60
            minsecmin = int(minsec)
            sec = int((minsec - minsecmin)*60)
            self.time_passed.config(text = "{m:02d} : {s:02d}".format(m=min,s=sec), fg = "red", bg = "black")
            self.time_passed.after(100, self.updatetime)


    def publish3(self):
        self.frame4.grid(row=1, column=1, sticky=N)
        self.frame10.grid(row=1, column=2, sticky=N)
        self.time_passed.grid()

    

class DataProcessing:
    def __init__(self, root, buffer, UDPClient, serverAddress):
        self.start_time = time.time()
        self.root = root
        self.buffer = buffer
        self.UDPClient = UDPClient
        self.serverAddress = serverAddress
        self.fig, self.ax = plt.subplots(2,2,figsize=(5, 4))
        self.frame5 = LabelFrame(root, text="Live Plot", padx=1, pady=1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame5)
        self.threading = True

        self.U1datatrim = []
        self.U3datatrim = []
        self.U4datatrim = []
        self.xdatatrim = []
        self.currenttrim = []
        self.pos_count = []

        self.t1 = threading.Thread(target = self.live_dat, daemon = True)
        self.t2 = threading.Thread(target = self.plot_data, daemon = True)
        self.t1.start()
        self.t2.start()
        self.t2.join()

        self.publish5()


    def publish5(self):
        self.frame5.grid(row=3, column=0, sticky=NE)
        self.canvas.get_tk_widget().grid()

    def plot_data(self):

        self.ax[0, 0].scatter(self.pos_count, self.U1datatrim)
        self.ax[0, 1].scatter(self.pos_count, self.U3datatrim)
        self.ax[1, 0].scatter(self.pos_count, self.U4datatrim)
        # self.ax[1,1].scatter(self.pos_count, self.xdatatrim)
        self.ax[1, 1].scatter(self.pos_count, self.currenttrim)

        self.ax[0, 0].set_title('U1 Temperature')
        self.ax[0, 1].set_title('U3 Temperature')
        self.ax[1, 0].set_title('U4 Temperature')
        # self.ax[1,1].set_title('X Acceleration')
        self.ax[1, 1].set_title('Current (Amps)')


    def live_dat(self):
        self.threading = True
        pos_count = 0
        msgfCli = 'Client'
        bytes2send = msgfCli.encode('utf-8')
        serverAddress = ('172.20.10.7', 2224)
        buffer = 2048
        UDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        file_path = 'output_current.csv'
        data_file = open(file_path, 'w')
        writer = csv.writer(data_file)

        while True:
            time.sleep(0.01)
            UDPClient.settimeout(5)
            try:
                UDPClient.sendto(bytes2send, serverAddress)
                data, address = UDPClient.recvfrom(buffer)
                line = data.decode('utf-8')
                print(line)
                pos_count += 1
                try: 
                    values = [float(x) for x in line.split(',')]
               
                    temp_values = values[:3]
                    acc_values = values[-3:]
                    #current_values = values[6]
                    voltage_values = values[6]
                    maxPoints = 50

                    U1data = temp_values[0]
                    U3data = temp_values[1]
                    U4data = temp_values[2]
                    xdata = acc_values[0]
                    #current = current_values
                    current = (5 * (voltage_values/1023) - 2.46) / 0.05
                    
    
                    try:
                        self.U1datatrim.append(U1data)
                        self.U3datatrim.append(U3data)
                        self.U4datatrim.append(U4data)
                        self.xdatatrim.append(xdata)
                        self.pos_count.append(pos_count)
                        self.currenttrim.append(current)
                        self.U1datatrim = self.U1datatrim[-maxPoints:]
                        self.U3datatrim = self.U3datatrim[-maxPoints:]
                        self.U4datatrim = self.U4datatrim[-maxPoints:]
                        self.xdatatrim = self.xdatatrim[-maxPoints:]
                        self.pos_count = self.pos_count[-maxPoints:]
                        self.currenttrim = self.currenttrim[-maxPoints:]
                        self.ax[0,0].cla()
                        self.ax[0,1].cla()
                        self.ax[1,0].cla()
                        self.ax[1,1].cla()
                    

                    except:
                        self.U1datatrim.append(U1data)
                        self.U3datatrim.append(U3data)
                        self.U4datatrim.append(U4data)
                        self.xdatatrim.append(xdata)
                        self.pos_count.append(pos_count)
                        self.currenttrim.append(current)
                        self.ax[0,0].cla()
                        self.ax[0,1].cla()
                        self.ax[1,0].cla()
                        self.ax[1,1].cla()
                        
                


                    # self.ax[0,0].scatter(self.pos_count, self.U1datatrim)
                    # self.ax[0,1].scatter(self.pos_count, self.U3datatrim)
                    # self.ax[1,0].scatter(self.pos_count, self.U4datatrim)
                    # #self.ax[1,1].scatter(self.pos_count, self.xdatatrim)
                    # self.ax[1,1].scatter(self.pos_count, self.currenttrim)
                    #
                    #
                    #
                    #
                    # self.ax[0,0].set_title('U1 Temperature')
                    # self.ax[0,1].set_title('U3 Temperature')
                    # self.ax[1,0].set_title('U4 Temperature')
                    # #self.ax[1,1].set_title('X Acceleration')
                    # self.ax[1,1].set_title('Current (Amps)')
                   


                    self.canvas.draw()
                    writer.writerow(values)
                    data_file.flush()


                except Exception as error:
                    print("Error received:", error)
                    pass

            except socket.timeout:
                print("Timeout Error")
                break
        data_file.close()


class SlideMotor():
    def __init__(self, root, buffer, UDPClient, serverAddress):
        self.root = root
        self.buffer = buffer
        self.UDPClient = UDPClient
        self.serverAddress = serverAddress
        self.frame6 = LabelFrame(root, text = "Motor Throttle = 0 ", padx=25, pady=25, fg= "white", bg="black")
        self.frame7 = Label(root, text = "Delay = --- microseconds", padx=15, pady=15, fg= "white", bg="black")
        self.frame8 = LabelFrame(root, text="Enter an Integer between -100 and 100", padx=50, pady=20, bg="black", fg= "white")
        self.textbox = Entry(self.frame8, width=50, fg="grey", bg="white")
        self.textbox.pack()
        self.textbox.bind("<Return>", self.callmotorspeed)
        self.motor = Scale(self.frame6, from_=-100, to=100, orient=HORIZONTAL, length=600, showvalue=0, tickinterval=10, resolution=1, command=self.motorspeed)
        self.motor.pack()
   
        self.publish6()

    
    def callmotorspeed(self,x):
        if digLock == False:
            v = self.textbox.get()
        else:
            v = 0
        try: 
            if int(v) > 100 or int(v) < -100:
                self.frame8.config(text = "WARNING: Entry is outside of bounds", fg="red")
            else: 
                self.frame8.config(text="Enter an Integer between -100 and 100", fg= "white")
                self.motor.set(v)
                self.motorspeed(v)
        except:
            self.frame8.config(text = "WARNING: Entry is not an integer", fg="red")

        

    def motorspeed(self,v):
        if digLock == False:
            self.frame6.config(text = "Motor Throttle (%) = " + v, fg= "white", bg = "black")
            
            min = 500     
            max = 2500      
            
            throttle = float(v)
            delay = int((throttle + 100)*(max - min)/200 + 500)
            delay_converted = int((throttle + 100)*5)

            delay_converted = str(delay_converted)
            self.delay_converted = delay_converted.encode('utf-8')
            time.sleep(0.01)
            self.UDPClient.sendto(self.delay_converted, self.serverAddress)
            self.frame7.config(text = "Delay = " + str(delay)  + " microseconds", font=("Helvectica", 10), fg= "white", bg = "black")
        
        else:
            pass
        

    def publish6(self):
        self.frame6.grid(row=2, column=4, sticky=N)
        self.frame7.grid(row=0, column=4, sticky=N)
        self.frame8.grid(row=1, column=4, sticky=N)
        self.motor.grid()


class ButtonsLA():
    def __init__(self, root, buffer, UDPClient, serverAddress):
        self.root = root
        self.buffer = buffer
        self.UDPClient = UDPClient
        self.serverAddress = serverAddress
        self.frame9 = LabelFrame(root, text = "Linear Actuator Control", padx=25, pady=25, fg= "white", bg="black")
        self.upButton = Button(self.frame9, text="UP", bg="grey", width=10,height=10)
        self.upButton.bind('<Button-1>', self.up)
        self.upButton.bind('<ButtonRelease-1>', self.stop)
        self.downButton = Button(self.frame9, text="DOWN", bg="grey", width=10,height=10)
        self.downButton.bind('<Button-1>', self.down)
        self.downButton.bind('<ButtonRelease-1>', self.stop)

        self.publish7()


    def up(self,x): 
        if digLock == False: 
                self.commandLinearActuator = 'UP'
                self.commandLinearActuator = self.commandLinearActuator.encode('utf-8')
                self.UDPClient.sendto(self.commandLinearActuator, self.serverAddress)
        else: 
            pass 
        
    def down(self,x):
        if digLock == False:
                self.commandLinearActuator = 'DOWN'
                self.commandLinearActuator = self.commandLinearActuator.encode('utf-8')
                self.UDPClient.sendto(self.commandLinearActuator, self.serverAddress)
        else: 
            pass


    def stop(self,x):
        if digLock == False:
            self.commandLinearActuator = 'NONE'
            self.commandLinearActuator = self.commandLinearActuator.encode('utf-8')
            self.UDPClient.sendto(self.commandLinearActuator, self.serverAddress)
        else:
             pass

    def publish7(self):
        self.frame9.grid(row=3, column=3, sticky=N)
        self.upButton.grid(row=4, column=3, sticky=N)
        self.downButton.grid(row=4, column=4, sticky=N)


def UpdateElapsedTime():
    global ElapsedTime
    ElapsedTime = int(time.time() - startNow + ElapsedTime)


if __name__ == "__main__":
    RootGUI()
    BUTTONS()
    RUNNING_TIMER()
    SlideMotor()
    ButtonsLA()
