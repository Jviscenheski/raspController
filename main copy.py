from time import sleep
from gpio import GPIO
import datetime 
from database import Database
import RPi.GPIO as gpioLib
import cv2
from vote_detection import VoteDetector
import pandas as pd

def moveBallot(direction, gp, conveyorTime):
    
    for i in range(0, conveyorTime):
        gp.stepperMotor.controlPort(direction)
        
        
def moveGate(gp):
    
    gp.lcdDisplay.writeInfo("Please insert", "your vote")
    gp.servoMotor.openGate()
    gp.lcdDisplay.writeInfo("Please confirm", "to close gate")
    while True:
        cg = input()
        if cg == "/":
            gp.servoMotor.closeGate()
            break
    
def insertVote(gp, vote_detector):
    # criar funcao para verificar se a criatura ja terminou de preencher o voto
    
    moveGate(gp)
    
    voteResult = None
    ballot_id = None
    vote_type = None
    tentatives = 0
        
    while (ballot_id is None or vote_type is None) and tentatives < 5:
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
                moveBallot('fechar', gp, conveyorTime=15)
                gp.lcdDisplay.writeInfo("Are you ready?", "Confirm?")
                ip = input()
                if ip == '/':
                    userWithVote = True
                    moveGate(gp)
        
        if ballot_id is not None:
            print("***********************")
            print(ballot_id)
            tentatives_cap = 0
            vote_list = []
            lastResult = None
            while tentatives_cap < 3:
                print("tentative_cap", str(tentatives_cap))
                ret, frame = cap.read()
                ballot_id, voteResult, vote_type = detectAndComputeVote(frame, vote_detector)
                if vote_type is not None:
                    if vote_type is 0:
                        lastResult = voteResult
                    vote_list.append(vote_type)
                    tentatives_cap += 1
            print(vote_list)
            vote_type = max(set(vote_list), key=vote_list.count)
            if vote_type is 0:
                voteResult = lastResult
                
        
                
        tentatives += 1
        print("tentatives", tentatives)
        print("ballot_id", ballot_id)
        print("voteResult",voteResult)
        print("vote_type", vote_type)

        cap.release()
            
    gp.led.turnOff(gp.led.yellowLed)
    if vote_type is not None:
        gp.lcdDisplay.writeInfo("Vote detected!", "")
    else:
        gp.lcdDisplay.writeInfo("Vote not", "detected")
    sleep(2)
    
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
            db.insertVote(str(ballot_id), voteResult, vote_type)
            db.setVoterStatus(voter['userId'], "complete")
            moveBallot('abrir', gp, conveyorTime=25)
            gp.led.turnOff(gp.led.greenLed)
            return 1
        elif voteConfirmation == '*':
            gp.lcdDisplay.writeInfo("Vote cancelled!", "")
            gp.led.turnOn(gp.led.redLed)
            moveBallot('fechar', gp, conveyorTime=25)
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
    gp.led.turnOff(gp.led.yellowLed)
    gp.lcdDisplay.writeInfo("Auth is done", "")
    db.setVoterStatus(voter, "auth")
    sleep(3)
    gp.lcdDisplay.writeInfo("Please fill your", "ballot")
    sleep(3)
    gp.led.turnOff(gp.led.greenLed)
    
    voteConfirmed = None
    #voteList = []
    #l  = 0
    while voteConfirmed is None:
        #while l < 3:
        ballot_id, voteResult, vote_type = insertVote(gp, vote_detector)
        #    voteList.append(vote_type)
        #    l += 1
        #if l[0] == l[1] and l[1] == l[2]:
        if vote_type is None:
            moveBallot('fechar', gp, conveyorTime=20)
        else:
            voteConfirmed = checkVote(gp, voteResult, db, ballot_id, voter, vote_type)

    print(ballot_id, voteConfirmed)
    
    
'''
def saveimg(path, imageName, img, convert=False):
    if convert:
        img = np.copy(img[..., ::-1])  # RGB 2 BGR
    cv2.imwrite(path+imageName, img)
'''

def getMode(lst):
    return max(set(lst), key=lst.count)
    
def detectAndComputeVote(frame, vote_detector):
    return_image, ballot_id, vote_type, valid_vote = vote_detector.executeDetectVotes(
            frame, draw=True)
    
    return ballot_id, valid_vote, vote_type
        
def recountVotes(db, gp, vote_detector):
    numberOfVotes = db.getVotes()
    votesDict = {}
    for i in range(0, numberOfVotes):
        while ballot_id is None or voteResult is None:
            gp.lcdDisplay.writeInfo("Analyzing vote "+str(i))
            gp.led.turnOn(gp.led.yellowLed)
            moveBallot('abrir', gp, conveyorTime=3)
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  480)
            ret, frame = cap.read()
            ballot_id, voteResult, vote_type = detectAndComputeVote(frame, vote_detector)
        
        votesDict['i'] = [ballot_id, voteResult]

    df = pd.DataFrame.from_dict(votesDict, orient='index', columns=['ballot_id', 'candidate'])
    print(df)

def main():
    gp = GPIO()
    db = Database()
    vote_labels = db.getCandidates()
    vote_detector = VoteDetector(vote_labels)
    
    loginErrorMssg = {0: ('Invalid finger', 'Try again'), 1:('Invalid finger', 'Try again'), 2:('Invalid finger', 'change method')}
    votesNeeded = db.getVoters()
    print("votesNeeded: ", votesNeeded)
    while True:
        
        isElectionTime = db.electionTime()
        
        if not isElectionTime:
            # se for antes, aguarda (msg no display e led vermelho piscando) -- watch dog
            #print("Waiting to start", "")
            gp.lcdDisplay.writeInfo("Election not", "available now")
            #gpioLi-b.output(18, True)
            gp.led.turnOn(gp.led.redLed)
            sleep(10)
        elif isElectionTime and votesNeeded:
            gp.led.turnOff(gp.led.redLed)
            gp.led.turnOn(gp.led.yellowLed)
            # quando der o hor??rio da elei????o e msg no display - aguardando pr??ximo voter
            # gp.lcdDisplay.writeInfo("Waiting for", "voter's finger")
            validVoter = None
            authTries = 0
            while validVoter is None:
                while authTries < 3:
                    # gp.led.turnOff(gp.led.yellowLed)
                    #print("Waiting for", "voter's finger")
                    gp.lcdDisplay.writeInfo("Waiting for", "voter's finger")
                    fingerResult = gp.fingerprintSensor.searchFinger()
                    validVoter = db.getVoter(str(fingerResult))   # verifica se o id ?? v??lido
                    print(validVoter)
                    #print(validVoter)
                    if validVoter is None: 
                        #print("Voter didn't", "recognized")
                        gp.lcdDisplay.writeInfo("Voter not", "recognized")
                        authTries += 1
                        sleep(3)
                    else:
                        if validVoter['status'] == 'pending':
                            initVotingProcess(gp, vote_detector, db, validVoter)
                        elif validVoter['status'] == "auth":
                            
                            #print("You're auth", "but didnt vote")
                            gp.lcdDisplay.writeInfo("Authenticated but", "did not vote")
                            sleep(3)
                        else:
                            gp.led.turnOff(gp.led.yellowLed)
                            gp.led.turnOn(gp.led.redLed)
                            #print("You already", "voted")
                            gp.lcdDisplay.writeInfo("You already", "voted")
                            sleep(3)
                else:
                    #print("Type id", "please")
                    gp.lcdDisplay.writeInfo("Type id", "please")
                    voterId = input()
                    validVoter = db.getVoter(voterId)   # verifica se o id ?? v??lido
                    if validVoter is not None:
                        authTries = 0
                        while authTries < 3:
                            #print("Type your", "password")
                            gp.lcdDisplay.writeInfo("Type your", "password")
                            voterPassword = input()
                            if voterPassword == validVoter['password']:
                                initVotingProcess(gp, vote_detector, db, validVoter)
                                break
                            else:
                                gp.led.turnOn(gp.led.redLed)
                                #print('Invalid password', loginErrorMssg[authTries][1])
                                gp.lcdDisplay.writeInfo('Invalid password', loginErrorMssg[authTries][1])
                                sleep(4)
                                gp.led.turnOff(gp.led.redLed)
                                authTries += 1
                        authTries = 0         
main()