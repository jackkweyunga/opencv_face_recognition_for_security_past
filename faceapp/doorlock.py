import serial
import time

from .speech import speak
from .settings import DOORLOCK_PORT


arduino = None

try:
    arduino = serial.Serial(port=DOORLOCK_PORT, baudrate=115200, timeout=.1)
except:
    pass

def write_read(x):
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = arduino.readline()
    return data

def open_door(flag: str):
    
    flag = str(flag)
    
    if arduino is not None:
        try:
            value = write_read(flag)
            print(f"log: {value}")
        except:
            print("Door System not connected")
        speak("Opening the door.")

