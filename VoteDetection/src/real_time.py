import cv2
from vote_detection import VoteDetector
from qr_code import QrCodeManager
import random

# frame = cv2.imread('/home/rafh/git/local/DetectCircle/src/hue2.png')
vote_labels = ['Vote3', 'Vote2', 'Vote1']

def saveimg(path, imageName, img, convert=False):
    if convert:
        img = np.copy(img[..., ::-1])  # RGB 2 BGR
    cv2.imwrite(path+imageName, img)
        
def getMode(lst):
    return max(set(lst), key=lst.count)


vote_detector = VoteDetector(vote_labels)
qr_code_manager = QrCodeManager()

valid_votes = []
while True:
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()

    qr_data = qr_code_manager.readQrCode(frame)

    if qr_data == 'ops':
        cap.release()
        print('Está de meme? Voto de cabeça para baixo, pô')
        continue
    
    img, vote = vote_detector.executeDetectVotes(frame, False)
    
    if isinstance(vote, list):
        valid_votes.append(vote[0])
    else:
        valid_votes.append(vote)

    if len(valid_votes) >= 2:
        valid_vote = getMode(valid_votes)
        print(valid_vote)
        # COLOCAR no BANCO COM VALID_VOTE E QR_DATA
        valid_votes = []
    
    # position = (150, 150)
    # cv2.putText(img, qr_data, position, cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0, 255), 6)
    img = vote_detector.detectBar(frame)

    # cv2.imshow('Pipa - Circle Detection', img)
    
    saveimg('src/ibagens/', ('barrinha' + str(random.randint(1, 100)) + '.jpg'), img, convert=False)
    cap.release()
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
