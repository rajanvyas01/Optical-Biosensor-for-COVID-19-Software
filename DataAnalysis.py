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

def f(x, *parameters):

    inten = np.zeros_like(x) + parameters[0]

    for i in range(1, len(parameters), 3):

        a = parameters[i]
        half = parameters[i+1]        
        wav = parameters[i+2]

        inten = inten + (a/(math.pi*half))*(half**2/((x-wav)**2+half**2))

    return inten

# Function Computes the Difference Between the Wavlength Data Points in the Data Set
def computeWavelengthIncr(x):

    minWavelength = np.min(x)
    maxWavelength = np.max(x)
    rangeWav = maxWavelength - minWavelength
    incr = rangeWav/len(x)

    return incr


def peakPositionIdentification(power, peakCount):

    # Smooth Peaks to Reduce Number of Peaks
    smoothedData = savgol_filter(power, 100, 2)
    peakguess, _ = find_peaks(-smoothedData, distance = int(len(power)/(peakCount+1)))

    return peakguess

def singlePeakFit(peakguess, wavelength, power, incr):

    distance = int(1.5/incr)
    if (peakguess+distance) > (len(wavelength)-1):
        maxPos = len(wavelength)-1
    else:
        maxPos = peakguess + distance
    
    if peakguess-distance < 0:
        minPos = 0
    else:
        minPos = peakguess - distance

    g0 = [np.mean(power[minPos:maxPos]), power[peakguess], 1., wavelength[peakguess]]

    try: 
        fitresults, pcov = optimize.curve_fit(f, wavelength[minPos:maxPos], power[minPos:maxPos], p0 = g0)
        fiterrors = np.sqrt(np.diag(pcov))
    except:
        print('Fit did Not Converge')
        fitresults = [-1, -1, -1, -1]
        fiterrors = [-1, -1, -1, -1]

    return fitresults, fiterrors

def setBounds(wavelength, peakPosition, halfWidth, incr):

    peakIndex = 0
    peakDiff = 10**9

    for i in range(0,len(wavelength)):

        if np.abs(peakPosition-wavelength[i]) < peakDiff:
            peakIndex = i
            peakDiff = np.abs(peakPosition-wavelength[i])

    inclusionWidth = int(7*halfWidth/incr)

    if (peakIndex+inclusionWidth) > (len(wavelength)-1):
            upperBound = len(wavelength)-1
    else:
        upperBound = peakIndex+inclusionWidth
    
    if (peakIndex-inclusionWidth) < 0:
        lowerBound = 0
    else:
        lowerBound = peakIndex-inclusionWidth

    return lowerBound, upperBound

def fitPeak(wavelength, power, numPeaks):

    # Increment of Data
    incr = computeWavelengthIncr(wavelength)

    # Set Expected Number of Resonace Peaks that Appear in the FSR
    numberPeaks = numPeaks

    # Position of Peak Points in the Data Set
    peakguess = peakPositionIdentification(power, numberPeaks)
    
    results = []
    resulterr = []
    # Fitting Single Peaks to Each Peak
    i = 0
    
    while i < len(peakguess):

        fitresults, fiterrors = singlePeakFit(peakguess[i], wavelength, power, incr)

        if fitresults[2] == -1:
            # Peak is Not Valid
            numberPeaks = numberPeaks - 1
            peakguess = np.delete(peakguess, i)
        else: 
            i = i+1
            results.append(fitresults)
            resulterr.append(fiterrors)

    results = np.array(results)
    resulterr = np.array(resulterr)

    return peakguess, results, resulterr


# Currently Defunct, Methodology will Not be used on Senior Design Project System
def backGroundElimination():
    # Setting Exclusion Points for Background Elimination
    exclusionPoints = []
    for i in range(0, numberPeaks):
        resultOfFit = results[i]
        halfWidth = resultOfFit[2]
        exclusionHalfWidth = int(7*halfWidth/incr)

        if (peakguess[i]+exclusionHalfWidth) > (len(wavelength)-1):
            maxPos = len(wavelength)-1
        else:
            maxPos = peakguess[i] + exclusionHalfWidth
        
        if peakguess[i]-exclusionHalfWidth < 0:
            minPos = 0
        else:
            minPos = peakguess[i] - exclusionHalfWidth

        exclusionPoints.append(minPos)
        exclusionPoints.append(maxPos)

    print(exclusionPoints)
    
    polyWavelengths = wavelength[0:exclusionPoints[0]]
    polyPower = power[0:exclusionPoints[0]]

    for i in range(1, len(exclusionPoints)-1, 2):
        polyWavelengths = np.concatenate([polyWavelengths, wavelength[exclusionPoints[i]:exclusionPoints[i+1]]])
        polyPower = np.concatenate([polyPower, power[exclusionPoints[i]:exclusionPoints[i+1]]])

    polyWavelengths = np.concatenate([polyWavelengths, wavelength[exclusionPoints[len(exclusionPoints)-1]:(len(wavelength)-1)]])
    polyPower = np.concatenate([polyPower, power[exclusionPoints[len(exclusionPoints)-1]:(len(wavelength)-1)]])

   
    # Polynomial Fit
    parameters = np.polyfit(polyWavelengths, polyPower, 4)
    polyEq = np.poly1d(parameters)
    print(polyEq)
    backgroundFit = polyEq(wavelength)
    
    plt.figure(figsize=(9,6))
    plt.plot(polyWavelengths,polyPower, linewidth=.5, label="Data")
    plt.plot(wavelength,backgroundFit, linewidth=.5, label="Fit")
    plt.legend(loc="upper right")
    plt.ylabel('Power')
    plt.xlabel('Wavelength (nm)')
    plt.title('450 nm Gap Fit')
    plt.grid()
    # plt.savefig('dis.jpg', bbox_inches='tight')
    plt.show()
    #plt.close()


    #Test with background elimination
    power = power - backgroundFit    

    
    # Test Lorentzian Non-Linear Least Squares Curve Fit
    g0 = [np.mean(power)]
    
    # Guess Parameters for Peak Finding
    for i in range(0, numberPeaks):
        g0 = np.append(g0, [power[peakguess[i]], 1., wavelength[peakguess[i]]])

    # Multiple Lorentz Fits to the Number of Peaks
    results2, pcov = optimize.curve_fit(f, wavelength, power, p0 = g0)
    print(results2)

    # Plotting Data and Fit
    y2 = f(wavelength, *results2)
    plt.figure(figsize=(9,6))

    # Peak Points from PeakFind
    plt.scatter(wavelength[peakguess], power[peakguess], label = "Peak Points")

    # Smoothed Line from Finding Peaks
    #plt.plot(wavelength,smoothedData, linewidth=.5, label="Smoothed Data")

    # Original Data
    plt.plot(wavelength,power, linewidth=.5, label="Data")
    # Fit Line
    plt.plot(wavelength,y2, linewidth=.5, label="Fit")
    
    # Residuals
    #plt.plot(wavelength,power - y2, linewidth=.5, label="Residuals")

    plt.legend(loc="upper right")
    plt.ylabel('Power')
    plt.xlabel('Wavelength (nm)')
    plt.title('440 nm Gap Fit Residuals')
    plt.grid()
    # plt.savefig('dis.jpg', bbox_inches='tight')
    plt.show()

def loadData(fileName):

    f = open(fileName, 'r')
    test = f.read()
    f.close()
    test2 = test.split(' ')
    test3 =[]

    # Putting in 32-bit hex format
    for i in range(0, len(test2), 2):
        test3.append(test2[i]+test2[i+1])

    # Identifying Data (Check to make sure datalength is right: Rajan: 8 Index, James: 9 Index)
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

    return wavelength, power

def loadDiffFormat(fileName):

    # Getting Input Data
    # Any Data Input Method Will Need to be Converted to Two Numpy Arrrays
    # Wavelength - X Axis Data
    # Power - Y Axis Data
    wavelength = []
    power = []
    file = open(fileName, 'r')
    
    data = file.readlines()

    for i in range(1, len(data)):
        
        line = data[i]
        dataPull = line.split('\t')
        wavelength.append(float(dataPull[0]))
        power.append(float(dataPull[1]))

    file.close()

    wavelength = np.array(wavelength)
    power = np.array(power)

    return wavelength, power


def allFiles():

    filesNames = []
    for filename in glob.glob(os.path.join(r'C:\Users\Maxwell\Desktop\Notes Old\Spring 2022\EE 464H\Data Analysis Program\4.14', '*.txt')):
            filesNames.append(filename) 

    return filesNames


def wavelengthShiftCalc(results1, results2, err1, err2):

    peaksOne = []
    peaksTwo = []

    for i in range(0, len(results1)):
        peaksOne.append(results1[i][3])

    for i in range(0, len(results2)):
        peaksTwo.append(results2[i][3])

    
    print(peaksOne)
    print(peaksTwo)
    
    if peaksOne[0]-peaksTwo[0] > 0:
        shiftInWavelength = peaksTwo[0]-peaksOne[1]
        fitUsedOne = 1
        fitUsedTwo = 0
    else:
        shiftInWavelength = -peaksOne[1]+peaksTwo[1]
        fitUsedOne = 1
        fitUsedTwo = 1

    return shiftInWavelength, fitUsedOne, fitUsedTwo
    


def analyzeData(file1 = 'valid.txt', file2 = 'valid.txt'):


    #files = allFiles()
    #randomNumber = random.randint(0, len(files)-1)

    wavelength, power = loadData(file1)    
    #wavelength, power = loadDiffFormat(files[randomNumber])
    peakguess1, result1, resulterr1 = fitPeak(wavelength, power, 3)
    wavelengthShifted, powerShifted = loadData(file2)
    #wavelengthShifted, powerShifted = loadDiffFormat(files[(random.randint(randomNumber, len(files)-1))])
    peakguess2, result2, resulterr2 = fitPeak(wavelengthShifted, powerShifted, 3)
    
    incr = computeWavelengthIncr(wavelength)
    wavelengthShift, usedOne, usedTwo = wavelengthShiftCalc(result1, result2, resulterr1, resulterr2)
    print(wavelengthShift)
    plt.figure(figsize=(9,6))

    plt.plot(wavelength,power, linewidth=.5, label="Water Cladding")
    fitCurve = f(wavelength[(int(peakguess1[usedOne]-1.5/incr)):(int(peakguess1[usedOne]+1.5/incr))], *(result1[usedOne]))
    plt.plot(wavelength[(int(peakguess1[usedOne]-1.5/incr)):(int(peakguess1[usedOne]+1.5/incr))],fitCurve, linewidth=.5, color='red', label="Fit")
    plt.scatter(wavelength[peakguess1], power[peakguess1], label = "Watter Cladding Peak Points")

    plt.plot(wavelengthShifted,powerShifted, linewidth=.5, label="Index Change Data")
    fitCurve = f(wavelength[(int(peakguess2[usedTwo]-1.5/incr)):(int(peakguess2[usedTwo]+1.5/incr))], *(result2[usedTwo]))
    plt.plot(wavelength[(int(peakguess2[usedTwo]-1.5/incr)):(int(peakguess2[usedTwo]+1.5/incr))],fitCurve, linewidth=.5, color='red')
    plt.scatter(wavelengthShifted[peakguess2], powerShifted[peakguess2], label = "Index Change Peak Points")
    plt.legend(loc="lower left")
    plt.ylabel('Power (dBm)')
    plt.xlabel('Wavelength (nm)')
    plt.title('Wavelength Shift Measurement Data')
    plt.grid()
    # plt.savefig('dis.jpg', bbox_inches='tight')
    plt.show()



    return wavelengthShift



    

if __name__ == "__main__": analyzeData()

