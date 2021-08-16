
try:
    import RPi.GPIO as gpioLib
    RASPI=True
except:
    from sim_raspi import RPiGPIO as gpioLib
    RASPI=False



class LED:

    def __init__(self):

        # leds
        self.greenLed = 15
        self.redLed = 18
        self.yellowLed = 14

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
    