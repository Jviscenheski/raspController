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


class LED:

    def __init__(self):

        # leds
        self.greenLed = 14
        self.redLed = 18
        self.yellowLed = 15

        self.initLEDS()     

    
    def initLEDS(self):
        gpioLib.setup(self.greenLed, gpioLib.OUT)
        gpioLib.output(self.greenLed, False)
        gpioLib.setup(self.redLed, gpioLib.OUT)
        gpioLib.output(self.redLed, False)
        gpioLib.setup(self.yellowLed, gpioLib.OUT)
        gpioLib.output(self.yellowLed, False)
    
    def turnOn(self, led):
        gpioLib.output(led, True)

    def turnOff(self, led):
        gpioLib.output(led, False)
    