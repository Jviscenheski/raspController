import cv2
from vote_detection_test import VoteDetector
from qr_code import QrCodeManager

# frame = cv2.imread('/home/rafh/git/local/DetectCircle/src/ballotAR.png')
# frame = cv2.imread('/home/rafh/git/local/DetectCircle/src/hue2.png')
vote_labels = ['Vote3', 'Vote2', 'Vote1']


def getMode(lst):
    return max(set(lst), key=lst.count)


vote_detector = VoteDetector(vote_labels)
qr_code_manager = QrCodeManager()

valid_votes = []
while True:
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()

    img, vote = vote_detector.executeDetectVotes(frame)

    # if isinstance(vote, list):
    #     valid_votes.append(vote[0])
    # else:
    #     valid_votes.append(vote)
    #
    # if len(valid_votes) >= 10:
    #     valid_vote = getMode(valid_votes)
    #     print(valid_vote)
    #     # COLOCAR no BANCO COM VALID_VOTE E QR_DATA
    #     valid_votes = []

    arucofound, return_image = vote_detector.detectAruco(frame)
    # ret = cv2.aruco.estimatePoseSingleMarkers(
    #     arucofound[0], 4, cameraMatrix=mtx, distCoeffs=dist)
    # (rvec, tvec) = (ret[0][0, 0, :], ret[1][0, 0, :])
    # print(rvec, tvec)
   # if len(arucofound[0]) != 0:
   #      for bbox, id in zip(arucofound[0], arucofound[1]):
   #          pass
    # cv2.circle(frame, (int(bbox[0][0][0]), int(bbox[0][0][1])), 1, (0, 0, 255), 8)
    # print(type(bbox), type(bbox[0]))
    # print(bbox, id[0])

    cv2.imshow('Pipa - Circle Detection', return_image)
    cap.release()
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
