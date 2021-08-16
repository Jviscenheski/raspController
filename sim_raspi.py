class RPiGPIO:
    def setmode(mode):
        print(f"Mode set to {mode}")
        pass
    def setup(pin, mode, initial=None):
        pins[pin] = initial if initial is not None else 0
        print(f"Pin {pin} as {mode}")
    def output(pin, value):
        pins[pin] = value
        #print(f"Pin {pin} set to {value}")
    def input(pin):
        print(f"Pin {pin} has value {pins[pin]}")
        pass
    def cleanup():
        print("Cleanup")
        pass
    BCM = 1

    IN = 0
    OUT = 1

    LOW = 0
    HIGH = 1

pins = {}

class pi:
    def set_PWM_frequency(self,pin,value):
        print(f"Pin {pin} frequency set to {value}")
        pins[pin] = value
    def set_servo_pulsewidth(self,pin,value):
        #print(f"Pin {pin} pulsewidth set to {value}")
        pins[pin] = value

class digitalio:
    def DigitalInOut(pin):
        pins[pin] = 0
        print(f"Pin {pin} as out")

class characterlcd:
    class Character_LCD_Mono: 
        def __init__(self,regSel, enable, d4, d5, d6, d7, cols, rows):
            print("LCD initialized")
            pass
        def clear(self):
            #print("LCD clear")
            pass
        message = ""

class board:
    D16=16
    D20=20
    D8=8
    D7=7
    D1=1
    D12=12

class PyFingerprint:
    def __init__(self,port,baudRate, address, password):
        print("Fingerprint sensor initialized")
        pass
    def verifyPassword(self):
        return True
    def readImage(self):
        return True
    def convertImage(self,buffer):
        pass
    def searchTemplate(self):
        print("Finger ID to be found:")
        result = int(input())
        return [result,100]

class cv:
    def detectAndComputeVote(frame, vote_detector):
        print("Ballot id to be found:")
        ballot_id = input()
        if ballot_id == "":
            ballot_id = None
        else:
            ballot_id = int(ballot_id)

        print("Vote result to be found:")
        voteResult = input()
        if voteResult == "":
            voteResult = None
        else:
            voteResult = vote_detector.vote_labels[int(voteResult)]

        print("Vote type to be found:")
        vote_type = input()
        if vote_type == "":
            vote_type = None
        else:
            vote_type = int(vote_type)

        return ballot_id, voteResult, vote_type
