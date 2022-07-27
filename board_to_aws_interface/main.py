"""
Some example code to test our serial port.
"""
import serial

COM_PORT = "COM3"
BAUD_RATE = 38400

with serial.Serial(COM_PORT, BAUD_RATE) as ser:
    if not ser.is_open:
        ser.open()
    while True:
        print(ser.readline().decode())
