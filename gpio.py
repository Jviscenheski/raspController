from fingerprintSensor import FingerprintSensor
import RPi.GPIO as gpioLib
import time
import board
import busio as io
import adafruit_mlx90614 as ada
from time import sleep
import smtplib
from datetime import datetime
import random
from stepperMotor import StepperMotor
from servoMotor import ServoMotor
from lcdDisplay import LCDDisplay
from picamera import PiCamera
from fingerprintSensor import FingerprintSensor


class GPIO:

    def __init__(self):

        # leds
        self.greenLed = 14
        self.redLed = 18
        self.yellowLed = 15

        self.stepperMotor = StepperMotor()

        self.stepperMotor = ServoMotor()

        self.lcdDisplay = LCDDisplay()   

        self.initLEDS() 

        self.cameraObj = PiCamera()  

        # rasp path to examples --> /usr/share/doc/python-fingerprint/examples 
        self.fingerprintSensor = FingerprintSensor()

    
    def initLEDS(self):
        gpioLib.setup(self.greenLed, gpioLib.OUT)
        gpioLib.output(self.greenLed, False)
        gpioLib.setup(self.redLed, gpioLib.OUT)
        gpioLib.output(self.redLed, False)
        gpioLib.setup(self.yellowLed, gpioLib.OUT)
    