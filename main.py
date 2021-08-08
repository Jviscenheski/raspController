from time import sleep
from gpio import GPIO
import datetime 
from database import Database
import RPi.GPIO as gpioLib
import cv2
from vote_detection import VoteDetector
from qr_code import QrCodeManager

conveyorTime = 30

def moveBallot(direction, gp):
    for i in range(0, conveyorTime):
        gp.stepperMotor.controlPort(direction)
        sleep(1)
    
def insertVote(gp):
    # criar funcao para verificar se a criatura ja terminou de preencher o voto
    gp.lcdDisplay.writeInfo("Please insert", "your vote")
    gp.servoMotor.openGate()
    for i in reversed(range(0, 10)):
        gp.lcdDisplay.writeInfo("Gate closes in ", str(i) + " seconds")
        sleep(1)
    gp.servoMotor.closeGate()
    voteResult = None
    qr_data = None
    valid_votes = []
    while qr_data is None and voteResult is None:
        gp.led.turnOn(gp.led.yellowLed)
        moveBallot('abrir', gp)
        ret, frame, cap = getFrames()
        if qr_data is None:
            qr_data = checkQrCode(frame, cap)
            if not qr_data:
                gp.lcdDisplay.writeInfo("Wrong side up", "Reinsert vote")
                moveBallot('fechar', gp)
        elif qr_data is not None and qr_data != 0:
            voteResult, valid_votes = detectAndComputeVote(frame, valid_votes)
            
    gp.led.turnOff(gp.led.yellowLed)
    return qr_data, voteResult

def checkVote(gp, voteResult):
    gp.lcdDisplay.writeInfo(voteResult, "Confirm?")
    voteConfirmation = input()
    if voteConfirmation:
        gp.led.turnOn(gp.led.greenLed)
        moveBallot('abrir', gp)
        gp.led.turnOff(gp.led.greenLed)
        return 1
    else:
        gp.led.turnOn(gp.led.redLed)
        moveBallot('fechar', gp)
        gp.led.turnOff(gp.led.redLed)
        return 0

def initVotingProcess(gp):
    gp.led.turnOn(gp.led.greenLed)
    gp.lcdDisplay.writeInfo("Auth is done", "")
    sleep(3)
    gp.lcdDisplay.writeInfo("Please fill your", "ballot")
    sleep(10)
    gp.led.turnOff(gp.led.greenLed)
    voteConfirmed = False
    while not voteConfirmed:
        qrResult, voteResult = insertVote(gp)
        voteConfirmed = checkVote(gp, voteResult)

def saveimg(path, imageName, img, convert=False):
    if convert:
        img = np.copy(img[..., ::-1])  # RGB 2 BGR
    cv2.imwrite(path+imageName, img)
        
def getMode(lst):
    return max(set(lst), key=lst.count)

def getFrames():
    
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    return ret, frame, cap

def checkQrCode(frame, cap):
    qr_data = qr_code_manager.readQrCode(frame)

    if qr_data == 'ops':
        cap.release()
        print('Está de meme? Voto de cabeça para baixo, pô')
        return 0
    return qr_data
    
def detectAndComputeVote(frame, valid_votes):
    
    img, vote = vote_detector.executeDetectVotes(frame, False)
    valid_vote = None
    
    if isinstance(vote, list):
        valid_votes.append(vote[0])
    else:
        valid_votes.append(vote)

    if len(valid_votes) >= 2:
        valid_vote = getMode(valid_votes)
        print(valid_vote)
        # COLOCAR no BANCO COM VALID_VOTE E QR_DATA
        valid_votes = []
    return valid_vote, valid_votes
        
def main():
    gp = GPIO()
    db = Database()
    
    while True:
        
        isElectionTime = db.electionTime()
        
        if not isElectionTime:
            # se for antes, aguarda (msg no display e led vermelho piscando) -- watch dog
            gp.lcdDisplay.writeInfo("Waiting to start", "")
            # gpioLib.output(18, True)
            gp.led.turnOn(gp.led.redLed)
            sleep(10)
        else:
            # quando der o horário da eleição e msg no display - aguardando próximo voter
            gp.lcdDisplay.writeInfo("Please type ", "your id")
            # get voter id - digita o RA (userId)
            validVoter = None
            while validVoter is None:
                voterId = input()
                validVoter = db.getVoter(voterId)   # verifica se o id é válido
                authTries = 0
                if validVoter is not None:
                    while authTries < 3:
                        # put your finger in there para autenticar o voter
                        gp.lcdDisplay.writeInfo("Waiting for", "voter's finger")
                        fingerResult = gp.fingerprintSensor.searchFinger()
                        if fingerResult == int(voterId):
                            initVotingProcess(gp)
                            break
                        else:
                            gp.lcdDisplay.writeInfo("Invalid finger", "Try again")
                            authTries += 1
                            sleep(2)
                    
                        if authTries >= 3:
                            authTries = 0
                            while authTries < 3:
                                gp.lcdDisplay.writeInfo("Type your", "password")
                                voterPassword = input()
                                if voterPassword == getVoterPassword(): ####ainda num fununfa
                                    initVotingProcess(gp)
                                    break
                                else:
                                    authTries += 1
                            authTries = 0
                                                           
                else:
                    gp.lcdDisplay.writeInfo("Voter not found", "Try again!")

main()