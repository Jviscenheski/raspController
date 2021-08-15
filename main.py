from time import sleep
from gpio import GPIO
import datetime 
from database import Database
import RPi.GPIO as gpioLib
import cv2
from vote_detection import VoteDetector

def moveBallot(direction, gp, conveyorTime):
    
    for i in range(0, conveyorTime):
        gp.stepperMotor.controlPort(direction)
        
        
def moveGate(gp):
    
    gp.lcdDisplay.writeInfo("Please insert", "your vote")
    gp.servoMotor.openGate()
    gp.lcdDisplay.writeInfo("Please confirm to", "close the gate")
    while True:
        cg = input()
        if cg == "'\'":
            gp.servoMotor.closeGate()
            break
    
def insertVote(gp, vote_detector):
    # criar funcao para verificar se a criatura ja terminou de preencher o voto
    
    moveGate(gp)
    
    voteResult = None
    ballot_id = None
    vote_type = None
        
    while ballot_id is None or voteResult is None:
        gp.lcdDisplay.writeInfo("Analyzing vote", "Wait detection")
        gp.led.turnOn(gp.led.yellowLed)
        moveBallot('abrir', gp, conveyorTime=3)
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  480)
        ret, frame = cap.read()
        ballot_id, voteResult, vote_type = detectAndComputeVote(frame, vote_detector)
        if ballot_id == 0:
            userWithVote = False
            while not userWithVote:
                gp.lcdDisplay.writeInfo("Vote is ", "upside down")
                #print('Virado para baixo')
                moveBallot('fechar', gp, conveyorTime=15)
                gp.lcdDisplay.writeInfo("Are you ready?", "Confirm?")
                ip = input()
                if ip == '/':
                    userWithVote = True
                    moveGate(gp)
                    
        print("ballot_id", ballot_id)
        print("voteResult",voteResult)
        print("vote_type", vote_type)

        cap.release()
            
    gp.led.turnOff(gp.led.yellowLed)
    print("Vote detected!")
    gp.lcdDisplay.writeInfo("Vote detected!", "")
    return ballot_id, voteResult, vote_type
 
def checkVote(gp, voteResult, db, ballot_id, voter, vote_type):
    
    while True:
        if vote_type == 1:
            voteResult = 'Null'
        elif vote_type == 2:
            voteResult = 'Blank'
            
        gp.lcdDisplay.writeInfo(voteResult, "Confirm?")
        voteConfirmation = input()
        if voteConfirmation == '/':
            gp.lcdDisplay.writeInfo("Vote confirmed!", "Thank you")
            gp.led.turnOn(gp.led.greenLed)
            db.insertVote(ballot_id, voteResult, vote_type)
            db.setVoterStatus(voter['userId'], "complete")
            moveBallot('abrir', gp, conveyorTime=20)
            gp.led.turnOff(gp.led.greenLed)
            return 1
        elif voteConfirmation == '*':
            #print('esteira para tras')
            gp.lcdDisplay.writeInfo("Vote canceled!", "")
            gp.led.turnOn(gp.led.redLed)
            moveBallot('fechar', gp, conveyorTime=15)
            gp.led.turnOff(gp.led.redLed)
            userWithVote = False
            while not userWithVote:
                gp.lcdDisplay.writeInfo("Are you ready?", " Please confirm")
                ip = input()
                if ip == '/':
                    userWithVote = True
            return None
        else:
            gp.lcdDisplay.writeInfo("Invalid option", "/-OK  *-NOK")       
        

def initVotingProcess(gp, vote_detector, db, voter):
    
    gp.led.turnOn(gp.led.greenLed)
    gp.lcdDisplay.writeInfo("Auth is done", "")
    db.setVoterStatus(voter, "auth")
    sleep(3)
    gp.lcdDisplay.writeInfo("Please fill your", "ballot")
    sleep(3)
    gp.led.turnOff(gp.led.greenLed)
    
    voteConfirmed = None
    while voteConfirmed is None:
        ballot_id, voteResult, vote_type = insertVote(gp, vote_detector)
        voteConfirmed = checkVote(gp, voteResult, db, ballot_id, voter, vote_type)
    
    print(ballot_id, voteConfirmed)
    
    

def saveimg(path, imageName, img, convert=False):
    if convert:
        img = np.copy(img[..., ::-1])  # RGB 2 BGR
    cv2.imwrite(path+imageName, img)
        
def getMode(lst):
    return max(set(lst), key=lst.count)
    
def detectAndComputeVote(frame, vote_detector):
    return_image, ballot_id, vote_type, valid_vote = vote_detector.executeDetectVotes(
            frame, draw=True)
    
    return ballot_id, valid_vote, vote_type
        
def main():
    gp = GPIO()
    db = Database()
    vote_labels = db.getCandidates()
    vote_detector = VoteDetector(vote_labels)
    
    loginErrorMssg = {0: ('Invalid finger', 'Try again'), 1:('Invalid finger', 'Try again'), 2:('Invalid finger', 'change method')}
    
    while True:
        
        isElectionTime = db.electionTime()
        
        if not isElectionTime:
            # se for antes, aguarda (msg no display e led vermelho piscando) -- watch dog
            gp.lcdDisplay.writeInfo("Waiting to start", "")
            # gpioLi-b.output(18, True)
            gp.led.turnOn(gp.led.redLed)
            sleep(10)
        else:
            gp.led.turnOff(gp.led.redLed)
            gp.led.turnOn(gp.led.yellowLed)
            # quando der o horário da eleição e msg no display - aguardando próximo voter
            # gp.lcdDisplay.writeInfo("Waiting for", "voter's finger")
            validVoter = None
            authTries = 0
            while validVoter is None:
                gp.lcdDisplay.writeInfo("Waiting for", "voter's finger")
                fingerResult = gp.fingerprintSensor.searchFinger()
                validVoter = db.getVoter(fingerResult)   # verifica se o id é válido
                if validVoter is None: 
                    gp.lcdDisplay.writeInfo("Voter didn't", "recognized")
                    sleep(3)
                else:
                    if authTries < 3:
                        if validVoter['status'] == 'pending':
                            initVotingProcess(gp, vote_detector, db, validVoter)
                        elif validVoter['status'] == "auth":
                            gp.led.turnOff(gp.led.yellowLed)
                            gp.led.turnOn(gp.led.redLed)
                            gp.lcdDisplay.writeInfo("You're auth", "but didnt vote")
                            sleep(3)
                        else:
                            gp.led.turnOff(gp.led.yellowLed)
                            gp.led.turnOn(gp.led.redLed)
                            gp.lcdDisplay.writeInfo("You already", "voted")
                            sleep(3)
                    else:
                        gp.lcdDisplay.writeInfo("Type id", "please")
                        voterId = input()
                        validVoter = db.getVoter(voterId)   # verifica se o id é válido
                        if validVoter is not None:
                            authTries = 0
                            while authTries < 3:
                                gp.lcdDisplay.writeInfo("Type your", "password")
                                voterPassword = input()
                                if voterPassword == validVoter['password']:
                                    initVotingProcess(gp, vote_detector, db, validVoter)
                                    break
                                else:
                                    gp.led.turnOn(gp.led.redLed)
                                    gp.lcdDisplay.writeInfo('Invalid password', loginErrorMssg[authTries][1])
                                    sleep(4)
                                    gp.led.turnOff(gp.led.redLed)
                                    authTries += 1
                                authTries = 0         
main()
