import pigpio

class ServoMotor:

    def __init__(self):

        self.servoPin = 2
        # create rpi instance
        self.rpi = pigpio.pi()
        # servomotors startup
        self.rpi.set_PWM_frequency(self.servoPin, 50)
        # set starting pen position, raise, lower, raise pen
        self.rpi.set_servo_pulsewidth(self.servoPin, 1000)

    def openGate(self):
        self.rpi.set_servo_pulsewidth(self.servoPin, 1000)

    def closeGate(self):
        self.rpi.set_servo_pulsewidth(self.servoPin, 1200)
    