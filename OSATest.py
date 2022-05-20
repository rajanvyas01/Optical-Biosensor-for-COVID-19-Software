import serial
import csv

with serial.Serial() as ser:
    ser.baudrate = 115200
    ser.port = '/dev/ttyUSB0'
    ser.open()
    ser.write(b'\x00\x00\x00\x03\x00\x00\x00\x2c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\xFF\xFF\xFF\xF6\x00\x00\x00\x00\xFF\xFF\xFB\xD4')

    data = []
    for i in range(10128):
        data.append(ser.read(2).hex())
        print(data[i])
        print('\n')
    
    with open("OSAoutput.txt", "w") as file:
        writer = csv.writer(file, delimiter=' ')
        writer.writerow(data)
    print(data)
    ser.close()
