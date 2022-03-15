# coding=utf-8
import time

modulname = "DataReader"
import socket
import sys

sys.path.insert(0, "lib/")
sys.path.insert(1, "lib/settings/")
import RPi.GPIO as GPIO


from lib.pins import v_LED1_Pin, v_LED2_Pin, v_PUMP1_Pin, v_PUMP2_Pin
from lib.functions import console, uibootscreen, \
    SensorData, processing, statusscreen, gpiosetup, komponententester, getsensordata
import websettings
import version

intervall = 5 #Min
intervall = intervall *60 # Sekunden

while True:
    console(modulname,"--Begin des Zyklus--")
    humidity, temperature, sensor_humitidy, sensor_temp = getsensordata()
    console(modulname,"--Ende des Zyklus--")
    time.sleep(intervall)

