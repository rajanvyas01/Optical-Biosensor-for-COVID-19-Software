from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QComboBox, QLineEdit
from PyQt5 import uic
import sys
import serial
import time
import csv
import numpy as np
import math as math
import matplotlib.pyplot as plt
import pandas as pd
from scipy import optimize
from scipy.signal import savgol_filter
from scipy.signal import find_peaks
import struct
import os,glob
import random
import DataAnalysis


class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        #load ui file
        uic.loadUi("SensorControls.ui", self)

        
        #define our widgets
        self.buttonID = self.findChild(QPushButton, "getIDButton")
        self.buttonCO = self.findChild(QPushButton, "currentOutputButton")
        self.buttonNO = self.findChild(QPushButton, "nextOutputButton")
        self.buttonRB = self.findChild(QPushButton, "readButton")
        self.buttonPB = self.findChild(QPushButton, "plotDataButton")
        self.buttonAB= self.findChild(QPushButton, "analyzeButton")
        self.lineFieldChannel = self.findChild(QLineEdit, "channelNumLine")
        self.switcherResponse = self.findChild(QLabel, "switcherResponseLabel")
        self.readDataLabel = self.findChild(QLabel,"readDataLabel")
        self.lineEditA = self.findChild(QLineEdit, "fileALine")
        self.lineEditB = self.findChild(QLineEdit, "fileBLine")
        self.lineEditPlot = self.findChild(QLineEdit, "plotLineEdit")
        self.shiftLabel = self.findChild(QLabel, "shiftLabel")

        #do the functions we need
        self.buttonID.clicked.connect(self.getTheID)
        self.buttonCO.clicked.connect(self.getCO)
        self.buttonNO.clicked.connect(self.go2NO)
        self.buttonRB.clicked.connect(self.readData)
        self.buttonPB.clicked.connect(self.plotData)
        self.buttonAB.clicked.connect(self.callanalyzeData)

        #show the app
        self.show()

    def getTheID(self):
        with serial.Serial() as ser:
            ser.baudrate = 115200
            ser.port = '/dev/ttyUSB0'
            ser.open()
            ser.write(b'\x49\x44\x3F\x0D')
            x = ser.readline()
            y = ser.readline()
            z = y.decode('UTF-8')
            self.switcherResponse.setText(z)
            ser.close()

    def getCO(self):
        with serial.Serial() as ser:
            ser.baudrate = 115200
            ser.port = '/dev/ttyUSB0'
            ser.open()
            ser.write(b'\x49\x31\x3F\x0D')
            x = ser.readline()
            y = ser.readline()
            z = y.decode('UTF-8')
            self.switcherResponse.setText("The current output channel is " + str(z))
            ser.close()
    
    def go2NO(self):
        lineEditValue = self.lineFieldChannel.text()
        with serial.Serial() as ser:
            ser.baudrate = 115200
            ser.port = '/dev/ttyUSB0'
            ser.open()
            if(lineEditValue == '0'):
                ser.write(b'\x49\x31\x20\x30\x0D')
                
            elif(lineEditValue == '1'):
                ser.write(b'\x49\x31\x20\x31\x0D')

            elif(lineEditValue == '2'):
                ser.write(b'\x49\x31\x20\x32\x0D')
        
            elif(lineEditValue == '3'):
                ser.write(b'\x49\x31\x20\x33\x0D')
            
            elif(lineEditValue == '4'):
                ser.write(b'\x49\x31\x20\x34\x0D')
            
            elif(lineEditValue == '5'):
                ser.write(b'\x49\x31\x20\x35\x0D')
            
            elif(lineEditValue == '6'):
                ser.write(b'\x49\x31\x20\x36\x0D')
            
            elif(lineEditValue == '7'):
                ser.write(b'\x49\x31\x20\x37\x0D')
            
            elif(lineEditValue == '8'):
                ser.write(b'\x49\x31\x20\x38\x0D')
            
            elif(lineEditValue == '9'):
                ser.write(b'\x49\x31\x20\x39\x0D')
            
            elif(lineEditValue == '10'):
                ser.write(b'\x49\x31\x20\x31\x30\x0D')
            
            elif(lineEditValue == '11'):
                ser.write(b'\x49\x31\x20\x31\x31\x0D')
            
            elif(lineEditValue == '12'):
                ser.write(b'\x49\x31\x20\x31\x32\x0D')
            
            elif(lineEditValue == '13'):
                ser.write(b'\x49\x31\x20\x31\x33\x0D')
            
            elif(lineEditValue == '14'):
                ser.write(b'\x49\x31\x20\x31\x34\x0D')
            
            elif(lineEditValue == '15'):
                ser.write(b'\x49\x31\x20\x31\x35\x0D')
            
            elif(lineEditValue == '16'):
                ser.write(b'\x49\x31\x20\x31\x36\x0D')
            
            else:
                self.switcherResponse.setText("Invalid Input, please try again.")
                ser.close()
                return
            
            #sleep to prevent race condition
            time.sleep(1)
            ser.write(b'\x49\x31\x3F\x0D')
            x = ser.readline()
            y = ser.readline()
            z = y.decode('UTF-8')
            self.switcherResponse.setText("The output channel has been changed to " + str(z))
            ser.close()

    def plotData(self):

        file2plot = self.lineEditPlot.text()

        def main():

            # Extracting OSA Data From Text File
            f = open(file2plot, 'r')
            test = f.read()
            f.close()
            test2 = test.split(' ')
            test3 =[]

            # Putting in 32-bit hex format
            for i in range(0, len(test2), 2):
                test3.append(test2[i]+test2[i+1])

            # Identifying Data (Check to make sure datalength is right: Rajan: 8 Index, James: 9 Index)
            #dynamic calculation of index below
            index = 0
            for k in range(20):
                if(test3[k] == '000009de'):
                    index = k
            print(index)

            dataLength = int(test3[index], 16)
            data = []
            print(dataLength)
            print(len(test3))
            # Converting Data
            for i in range(index + 1, dataLength*2+index+1):
                number = struct.unpack('!f', bytes.fromhex(test3[i]))[0]
                data.append(number)

            power = np.array(data[:(len(data)//2)])
            frequency = np.array(data[(len(data)//2):])
            frequency = (frequency)*1000
            # Convert Frequencys To Wavelength
            # Speed of Light c
            c = 299792458
            wavelength = (c/frequency)

            plt.figure(figsize=(9,6))
            plt.plot(wavelength,power, linewidth=.5, label="Data")
            plt.legend(loc="upper right")
            plt.ylabel('Power')
            plt.xlabel('Wavelength (nm)')
            plt.title('Data From OSA')
            plt.grid()
            # plt.savefig('dis.jpg', bbox_inches='tight')
            plt.show()

        if __name__ == "__main__": main()

    def readData(self):
        self.readDataLabel.setText("Processing Data...")
        QApplication.processEvents()

        with serial.Serial() as ser:
            ser.baudrate = 115200
            ser.port = '/dev/ttyUSB0'
            ser.open()
            ser.write(b'\x00\x00\x00\x03\x00\x00\x00\x2c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\xFF\xFF\xFF\xF6\x00\x00\x00\x00\xFF\xFF\xFB\xD4')

            #code to get data length from osa message
            x = ser.read(6)
            x = ser.read(2)
            y = int(x.hex(), 16)
            data = ['0000','0003','0000', x.hex()]

            for i in range((y-8)//2):
                data.append(ser.read(2).hex())
    
            with open("OSAoutput.txt", "w") as file:
                writer = csv.writer(file, delimiter=' ')
                writer.writerow(data)
            print(data)
            ser.close()

        time.sleep(1)
        self.readDataLabel.setText("OSAoutput.txt created!")

    def callanalyzeData(self):
        self.readDataLabel.setText("Calculating...")
        QApplication.processEvents()
        Afile = self.lineEditA.text()
        Bfile = self.lineEditB.text()
        shift = DataAnalysis.analyzeData(Afile, Bfile)
        value = round(shift, 3)
        time.sleep(1)
        self.readDataLabel.setText("The Shift is " + str(value) + " nm")


#initialize
app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()