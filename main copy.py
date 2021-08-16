try:
    import RPi.GPIO as gpioLib
    RASPI = True   
    CVXUNXO = False 
except:
    RASPI=False
    CVXUNXO = True
    import sim_raspi
    print("Rodando simulação")
from time import sleep
from gpio import GPIO
import datetime 
from database import Database
import cv2
from vote_detection import VoteDetector
import pandas as pd



def moveBallot(direction, gp, conveyorTime):
    print("Conveyor belt is moving")
    if RASPI is False:
        conveyorTime = 0
    for i in range(0, conveyorTime):
        gp.stepperMotor.controlPort(direction)
    print("Conveyor belt has stopped")
        
        
def moveGate(gp):
    gp.lcdDisplay.writeInfo("Please insert", "your vote")
    gp.servoMotor.openGate()
    sleep(1)
    gp.lcdDisplay.writeInfo("Please confirm", "to close gate")
    while True:
        print("Waiting input")
        cg = input()
        if cg == "/":
            gp.servoMotor.closeGate()
            break

def ballotUpsideDown(gp):
    userWithVote = False
    while not userWithVote:
        gp.lcdDisplay.writeInfo("Vote is", "upside down")
        moveBallot('tras', gp, conveyorTime=15)
        gp.lcdDisplay.writeInfo("Are you ready?", "Confirm?")
        print("Waiting input")
        ip = input()
        if ip == '/':
            userWithVote = True
            moveGate(gp)

def insertVote(gp, vote_detector):
    moveGate(gp)
    
    voteResult = None
    ballot_id = None
    vote_type = None
    tentatives = 0
    while (ballot_id is None or vote_type is None) and tentatives < 5:
        gp.lcdDisplay.writeInfo("Analyzing vote", "Wait detection")
        gp.led.turnOn(gp.led.yellowLed)
        moveBallot('frente', gp, conveyorTime=3)
        if not CVXUNXO:
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  480)
            ret, frame = cap.read()
            ballot_id, voteResult, vote_type = detectAndComputeVote(frame, vote_detector)
        else:
            frame = None
            ballot_id, voteResult, vote_type = sim_raspi.cv.detectAndComputeVote(frame, vote_detector)

        if ballot_id == 0:
            ballotUpsideDown(gp)
            tentatives = 0
            ballot_id, voteResult, vote_type = None, None, None

        elif ballot_id is not None:
            print("***********************")
            print("ballot_id",ballot_id)
            tentatives_cap = 0
            typeNoneCount = 0
            vote_list = []
            lastResult = None
            #captura 3 vote types válidos ou 5 None
            while tentatives_cap < 3 and typeNoneCount < 5:
                if not CVXUNXO:
                    ret, frame = cap.read()
                    ballot_id, voteResult, vote_type = detectAndComputeVote(frame, vote_detector)
                else:
                    frame = None
                    ballot_id, voteResult, vote_type = sim_raspi.cv.detectAndComputeVote(frame, vote_detector)
                print("tentative_cap", str(tentatives_cap))
                print("ballot_id", ballot_id)
                print("voteResult",voteResult)
                print("vote_type", vote_type)
                if vote_type is not None:
                    if vote_type == 0:
                        lastResult = voteResult
                    vote_list.append(vote_type)
                    tentatives_cap += 1
                else:
                    typeNoneCount += 1
            print("vote_list",vote_list)
            if (typeNoneCount >= 5):
                vote_type = max(set(vote_list), key=vote_list.count)
                if vote_type == 0:
                    voteResult = lastResult
                else:
                    vote_type = None
                
        
                
            tentatives += 1
            print("tentatives", tentatives)
            print("ballot_id", ballot_id)
            print("voteResult",voteResult)
            print("vote_type", vote_type)

            if not CVXUNXO:
                cap.release()
            
    gp.led.turnOff(gp.led.yellowLed)
    if vote_type is not None:
        gp.lcdDisplay.writeInfo("Vote detected!", "")
    else:
        gp.lcdDisplay.writeInfo("Vote not", "detected")
    sleep(2)
    
    return ballot_id, voteResult, vote_type
 
def voteConfirmed(gp, voteResult, db, ballot_id, voter, vote_type):
    gp.lcdDisplay.writeInfo("Vote confirmed!", "Thank you")
    gp.led.turnOn(gp.led.greenLed)
    db.insertVote(str(ballot_id), voteResult, vote_type)
    db.setVoterStatus(voter['userId'], "complete")
    moveBallot('frente', gp, conveyorTime=25)
    gp.led.turnOff(gp.led.greenLed)
    return 1

def voteCancelled(gp):
    gp.lcdDisplay.writeInfo("Vote cancelled!", "")
    gp.led.turnOn(gp.led.redLed)
    moveBallot('tras', gp, conveyorTime=25)
    gp.led.turnOff(gp.led.redLed)
    userWithVote = False
    while not userWithVote:
        gp.lcdDisplay.writeInfo("Are you ready?", "Please confirm")
        print("Waiting input")
        ip = input()
        if ip == '/':
            userWithVote = True
    return None

def checkVote(gp, voteResult, db, ballot_id, voter, vote_type):
    
    while True:
        if vote_type == 1:
            voteResult = 'Null'
        elif vote_type == 2:
            voteResult = 'Blank'

        gp.lcdDisplay.writeInfo(voteResult, "Confirm?")
        print("Waiting input")
        voteConfirmation = input()
        if voteConfirmation == '/':
            return voteConfirmed(gp, voteResult, db, ballot_id, voter, vote_type)
        elif voteConfirmation == '*':
            return voteCancelled(gp)
            
        else:
            gp.lcdDisplay.writeInfo("Invalid option", "/-OK  *-NOK")       
        

def initVotingProcess(gp, vote_detector, db, voter):
    
    gp.led.turnOn(gp.led.greenLed)
    gp.led.turnOff(gp.led.yellowLed)
    gp.lcdDisplay.writeInfo("Please fill your", "ballot")
    sleep(3)
    gp.led.turnOff(gp.led.greenLed)
    
    voteConfirmed = None
    while voteConfirmed is None:
        ballot_id, voteResult, vote_type = insertVote(gp, vote_detector)
        if vote_type is None:
            gp.lcdDisplay.writeInfo("Returning your", "vote")
            moveBallot('tras', gp, conveyorTime=20)
        else:
            ballotFound = db.findBallotId(str(ballot_id))
            if ballotFound is None:                
                voteConfirmed = checkVote(gp, voteResult, db, ballot_id, voter, vote_type)
            else:
                gp.lcdDisplay.writeInfo("Invalid ballot", "Insert another")
                moveBallot('tras', gp, conveyorTime=20)
    
    
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

def recountVoteNotDetected(gp):
    gp.lcdDisplay.writeInfo("Returning the", "vote")
    moveBallot('tras', gp, conveyorTime=20)

def recountBallotIDNotFound(gp):
    gp.lcdDisplay.writeInfo("Invalid ballot", "Not found")
    moveBallot('tras', gp, conveyorTime=20)

def recountBallotIDDuplicate(gp):
    gp.lcdDisplay.writeInfo("Invalid ballot", "Duplicate")
    moveBallot('tras', gp, conveyorTime=20)

def recountSaveBallot(gp,db,ballot_id,voteResult,vote_type):
    gp.led.turnOn(gp.led.greenLed)
    db.insertVoteRecount(str(ballot_id), voteResult, vote_type)
    moveBallot('frente', gp, conveyorTime=25)
    gp.led.turnOff(gp.led.greenLed)

def recountVotes(gp, db, vote_detector): 
    gp.lcdDisplay.writeInfo("Starting recount", "mode")  
    db.votesRecountEmpty()

    insertNewVote = None
    while insertNewVote != "*":
        ballot_id, voteResult, vote_type = insertVote(gp, vote_detector)
        if vote_type is None:
            recountVoteNotDetected(gp)
        else:   
            ballotFound = db.findBallotId(str(ballot_id))
            if ballotFound is not None:                
                recountBallotFound = db.findRecountBallotId(str(ballot_id))
                if recountBallotFound is None:
                    recountSaveBallot(gp,db,ballot_id,voteResult,vote_type)
                else:
                    recountBallotIDDuplicate(gp)
            else: 
                recountBallotIDNotFound(gp)
        gp.lcdDisplay.writeInfo("Insert another", "vote?")
        print("Waiting for input")
        insertNewVote = input()

    print(ballot_id, voteConfirmed)

    db.finishRecount()
    '''
    numberOfVotes = db.getVotes()
    votesDict = {}
    for i in range(0, numberOfVotes):
        while ballot_id is None or voteResult is None:
            gp.lcdDisplay.writeInfo("Analyzing vote "+str(i))
            gp.led.turnOn(gp.led.yellowLed)
            moveBallot('frente', gp, conveyorTime=3)
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  480)
            ret, frame = cap.read()
            ballot_id, voteResult, vote_type = detectAndComputeVote(frame, vote_detector)
        
        votesDict['i'] = [ballot_id, voteResult]

    df = pd.DataFrame.from_dict(votesDict, orient='index', columns=['ballot_id', 'candidate'])
    print(df)
    '''

def beforeElectionRoutine(gp):
    gp.lcdDisplay.writeInfo("Waiting for", "election start")
    gp.led.turnOn(gp.led.redLed)
    sleep(10)

def validVoterFound(gp, db, validVoter):
    if validVoter['status'] == 'pending':
        gp.lcdDisplay.writeInfo("Voter is", "authenticated")
        db.setVoterStatus(validVoter["userId"], "auth")
        sleep(2)
        return True, validVoter
    elif validVoter['status'] == "complete":                
        gp.led.turnOff(gp.led.yellowLed)
        gp.led.turnOn(gp.led.redLed)
        gp.lcdDisplay.writeInfo("You already", "voted")
        sleep(3)                    
    else:
        print("Se caiu aqui deu ruim")
        gp.lcdDisplay.writeInfo("Authenticated but", "did not vote")
        sleep(3)
    return True, None

def fingerAuth(gp,db,vote_detector):
    authTries = 0
    while authTries < 3:
        gp.lcdDisplay.writeInfo("Waiting for", "voter's finger")
        fingerResult = gp.fingerprintSensor.searchFinger()
        validVoter = db.getVoter(str(fingerResult))   # verifica se o id é válido
        print(validVoter)
        if validVoter is None: 
            gp.lcdDisplay.writeInfo("Voter not", "recognized")
            authTries += 1
            sleep(3)
        else:
            return validVoterFound(gp,db,validVoter)
    return False, None

def keypadAuth(gp,db,vote_detector):
    authTries = 0
    while authTries < 3:
        gp.lcdDisplay.writeInfo("Type id", "please")
        print("Waiting for input")
        voterId = input()
        validVoter = db.getVoter(voterId)   # verifica se o id é válido
        print(validVoter)
        if validVoter is None:
            gp.lcdDisplay.writeInfo("Voter not", "found")
            authTries += 1
            sleep(3)
        else:            
            gp.lcdDisplay.writeInfo("Type your", "password")
            print("Waiting for input")
            voterPassword = input()
            if voterPassword == validVoter['password']:
                return validVoterFound(gp,db,validVoter)
            else:
                gp.led.turnOn(gp.led.redLed)
                gp.lcdDisplay.writeInfo('Invalid password', "")
                sleep(3)
                gp.led.turnOff(gp.led.redLed)
                authTries += 1
    return False, None

def duringElectionRoutine(gp,db,vote_detector):
    
    gp.led.turnOff(gp.led.redLed)
    gp.led.turnOn(gp.led.yellowLed)
    auth, validVoter = fingerAuth(gp,db,vote_detector)
    if auth is False:
        keypadAuth()

    if auth is True and validVoter is not None:
        initVotingProcess(gp, vote_detector, db, validVoter)
            


def afterElectionRoutine(gp,db,vote_detector):
    mode, alreadyRecounted = db.getRecountMode()

    if alreadyRecounted:
        gp.lcdDisplay.writeInfo("Recount", "finished")
    elif mode:        
        recountVotes(gp,db,vote_detector)
    else:
        gp.lcdDisplay.writeInfo("Election", "finished")

    sleep(10)
    
def main():
    gp = GPIO()
    db = Database()
    vote_labels = db.getCandidates()
    vote_detector = VoteDetector(vote_labels)
    
    while True:
        
        beforeElection, afterElection = db.electionTime()
        duringElection = not beforeElection and not afterElection
        print(beforeElection, afterElection, duringElection)
        if beforeElection is True:
            beforeElectionRoutine(gp)
            
        elif duringElection:
            votesNeeded = db.getVoters()
            print("votesNeeded: ", votesNeeded)
            if votesNeeded != 0:   
                duringElectionRoutine(gp,db,vote_detector)
            else:
                gp.lcdDisplay.writeInfo("All votes", "counted")
                sleep(10)

        elif afterElection:
            afterElectionRoutine(gp,db,vote_detector)

        else:
            print("Se chegou aqui deu ruim")


main()