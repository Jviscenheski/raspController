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
from led import LED


class GPIO:

    def __init__(self):

        self.led = LED()
        
        self.stepperMotor = StepperMotor()

        self.servoMotor = ServoMotor()

        self.lcdDisplay = LCDDisplay()   

        self.cameraObj = PiCamera()  

        # rasp path to examples --> /usr/share/doc/python-fingerprint/examples 
        self.fingerprintSensor = FingerprintSensor()
    
    