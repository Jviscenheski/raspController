import pigpio
from time import sleep

class ServoMotor:

    def __init__(self):

        self.servoPin = 2
        # create rpi instance
        self.rpi = pigpio.pi()
        # servomotors startup
        self.rpi.set_PWM_frequency(self.servoPin, 50)
        # set starting pen position, raise, lower, raise pen
        # self.rpi.set_servo_pulsewidth(self.servoPin, 1000)

    def openGate(self):
        i = 1800
        while i >= 1000:
            self.rpi.set_servo_pulsewidth(self.servoPin, i)
            sleep(0.02)
            i -= 20
            
            

    def closeGate(self):
        i = 1000
        while i <= 1800:
            self.rpi.set_servo_pulsewidth(self.servoPin, i)
            sleep(0.02)
            i += 20
    