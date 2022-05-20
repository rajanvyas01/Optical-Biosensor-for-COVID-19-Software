import numpy as np
import math as math
import matplotlib.pyplot as plt
import pandas as pd
from scipy import optimize
from scipy.signal import savgol_filter
from scipy.signal import find_peaks
import struct

def main():

    # Extracting OSA Data From Text File
    f = open('valid.txt', 'r')
    test = f.read()
    f.close()
    test2 = test.split(' ')
    test3 =[]

    # Putting in 32-bit hex format
    for i in range(0, len(test2), 2):
        test3.append(test2[i]+test2[i+1])

    # Identifying Data (Check to make sure datalength is right: Rajan: 8 Index, James: 9 Index)
    index = 11
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

