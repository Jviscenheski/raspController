import RPi.GPIO as gpioLib
import time

class StepperMotor:

    def __init__(self):

        self.stepperMotorA1 = 25
        self.stepperMotorA2 = 22
        self.stepperMotorB1 = 23
        self.stepperMotorB2 = 24

        gpioLib.setup(self.stepperMotorA1, gpioLib.OUT)
        gpioLib.output(self.stepperMotorA1, False)
        gpioLib.setup(self.stepperMotorA2, gpioLib.OUT)
        gpioLib.output(self.stepperMotorA2, False)
        gpioLib.setup(self.stepperMotorB1, gpioLib.OUT)
        gpioLib.output(self.stepperMotorB1, False)
        gpioLib.setup(self.stepperMotorB2, gpioLib.OUT)
        gpioLib.output(self.stepperMotorB2, False)


    def controlPort(self, direction=None):
            
        StepPins = [self.stepperMotorA1, self.stepperMotorA2, self.stepperMotorB1, self.stepperMotorB2]
        StepCount=8
        Seq = [[1,0,0,1],
           [1,0,0,0],
           [1,1,0,0],
           [0,1,0,0],
           [0,1,1,0],
           [0,0,1,0],
           [0,0,1,1],
           [0,0,0,1]]
        
        if direction=='abrir':
            self.forward()
        else:
            self.backwards()

    def setStep(self, w1, w2, w3, w4):
        gpioLib.output(self.stepperMotorA1, w1)
        gpioLib.output(self.stepperMotorA2, w2)
        gpioLib.output(self.stepperMotorB1, w3)
        gpioLib.output(self.stepperMotorB2, w4)
    
    def forward(self):
        Seq = [[1,0,0,1],
           [1,0,0,0],
           [1,1,0,0],
           [0,1,0,0],
           [0,1,1,0],
           [0,0,1,0],
           [0,0,1,1],
           [0,0,0,1]]
        for i in range(256):
            for j in range(8):
                self.setStep(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
                time.sleep(0.0007)

    def backwards(self):
        Seq = [[1,0,0,1],
           [1,0,0,0],
           [1,1,0,0],
           [0,1,0,0],
           [0,1,1,0],
           [0,0,1,0],
           [0,0,1,1],
           [0,0,0,1]]
        for i in range(256):
            for j in reversed(range(8)):
                self.setStep(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
                time.sleep(0.0007)          
