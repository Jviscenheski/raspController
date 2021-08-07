from time import sleep
from gpio import GPIO
import datetime 

conveyorTime = 30

def insertVote(gp):
    # criar função para verificar se a criatura já terminou de preencher o voto
    gp.lcdDisplay.writeInfo("Please insert", "your vote")
    gp.servoMotor.openGate()
    for i in reversed(range(0, 10)):
        gp.lcdDisplay.writeInfo("Gate closes in ", str(i) + "seconds")
        sleep(1)
    gp.servoMotor.closeGate()
    qrResult = None
    voteResult = None
    while not qrResult and not voteResult:
        gp.led.turnOn(gp.led.yellowLed)
        gp.stepperMotor.controlPort(direction='abrir')
        qrResult = None
        voteResult = None

    gp.led.turnOff(gp.led.yellowLed)
    return qrResult, voteResult

def checkVote(gp, voteResult):
    gp.lcdDisplay.writeInfo(voteResult, "Confirm?")
    voteConfirmation = input()
    if voteConfirmation:
        gp.led.turnOn(gp.led.greenLed)
        for i in range(0, conveyorTime):
            gp.stepperMotor.controlPort(direction='abrir')
            sleep(1)
        gp.led.turnOff(gp.led.greenLed)
        return 1
    else:
        gp.led.turnOn(gp.led.redLed)
        for i in range(0, conveyorTime):
            gp.stepperMotor.controlPort(direction='fechar')
            sleep(1)
        gp.led.turnOff(gp.led.redLed)
        return 0

def initVotingProcess(gp):
    gp.led.turnOn(gp.led.greenLed)
    gp.lcdDisplay.writeInfo("Auth is done")
    sleep(3)
    gp.lcdDisplay.writeInfo("Please fill your", "ballot")
    sleep(10)
    gp.led.turnOff(gp.led.greenLed)
    while not voteConfirmed:
        qrResult, voteResult = insertVote(gp)
        voteConfirmed = checkVote(gp, voteResult)


def main():

    while True:
        gp = GPIO()

        # pega o horário das eleições do banco e compara com o local
        electionScheduleStart = None
        electionScheduleEnd = None
        currentTime = datetime.now()

        if currentTime < electionScheduleStart:
            # se for antes, aguarda (msg no display e led vermelho piscando) -- watch dog
            gp.lcdDisplay.writeInfo("Waiting to start")
            gp.led.turnOn(gp.led.redLed)
        elif currentTime >= electionScheduleStart and currentTime < electionScheduleEnd:
            # quando der o horário da eleição e msg no display - aguardando próximo voter
            gp.lcdDisplay.writeInfo("Please type", "your id")
            # get voter id - digita o RA (userId)
            voterId = input()
            validVoter = None   # verifica se o id é válido
            authTries = 0
            if validVoter:
                while authTries < 3:
                    # put your finger in there para autenticar o voter
                    gp.lcdDisplay.writeInfo("Waiting for", "voter's finger")
                    fingerResult = gp.fingerprintSensor.searchFinger()
                    if fingerResult == voterId:
                        initVotingProcess(gp)
                        break
                    else:
                        authTries += 1
                
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
                gp.lcdDisplay.writeInfo("Voter not found")

main()