import cv2
from vote_detection import VoteDetector

# frame = cv2.imread('/home/rafh/git/local/DetectCircle/src/ballotAR.png')
# frame = cv2.imread('/home/rafh/git/local/DetectCircle/src/hue2.png')
vote_labels = ['Vote3', 'Vote2', 'Vote1']


def getMode(lst):
    return max(set(lst), key=lst.count)


vote_detector = VoteDetector(vote_labels)


def execute():
    valid_votes = []
    while True:
        # for i in range(10):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  480)
        ret, frame = cap.read()
        

        return_image, ballot_id, vote_type, valid_vote = vote_detector.executeDetectVotes(
            frame, draw=True)

        # print(ballot_id, vote_type, valid_vote)

        print('Ballot id: ', ballot_id)

        print('Vote: ', valid_vote)

        # if ballot_id is None:
        #     cv2.imshow('Pipa - Circle Detection', frame)
        #     cap.release()
        #     continue
        # elif ballot_id == 0:
        #     # VOLTA
        #     pass
        # else:
        if valid_vote is not None:
            valid_votes.append(valid_vote)

        # print(valid_votes)

        # if len(valid_votes) >= 3:
        #     print('Valid vote: ' + getMode(valid_votes))
        #     valid_votes = []

        cv2.imshow('Pipa - Circle Detection', return_image)
        cap.release()
        if cv2.waitKey(1) == ord('q'):
            break


execute()
cv2.destroyAllWindows()
# vote_detector = VoteDetector(vote_labels)
#
# valid_votes = []
# while True:
#     cap = cv2.VideoCapture(0)
#     ret, frame = cap.read()
#
#     return_image, ballot_id, vote_type, valid_vote = vote_detector.executeDetectVotes(frame)
#
#     if ballot_id is None:
#         continue
#     elif ballot_id == 0:
#         # VOLTA
#         pass
#     else:
#         valid_votes.append(valid_vote)
#
#     if len(valid_votes) >= 5:
#         print('Valid vote: ' + getMode(valid_votes))
#         valid_votes = []
#
#     cv2.imshow('Pipa - Circle Detection', return_image)
#     cap.release()
#     if cv2.waitKey(1) == ord('q'):
#         break
#
# cv2.destroyAllWindows()
