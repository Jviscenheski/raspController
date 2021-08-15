import cv2
import numpy as np
import math
from camera_calibration import CameraCalibrator


IMAGES_PATH = '/home/rafh/git/local/DetectCircle/images/'


class Marker:
    def __init__(self, bbox, id, rvec, tvec, rmat, rotation):
        self.bbox = bbox
        self.id = id
        self.rvec = rvec
        self.tvec = tvec
        self.rmat = rmat
        self.rotation = rotation


class VoteDetector:

    vote_labels = []
    calibrator = CameraCalibrator()

    def __init__(self, vote_labels):
        self.calibrator.calibrate()
        self.vote_labels = vote_labels

    def saveimg(self, path, imageName, img, convert=False):
        if convert:
            img = np.copy(img[..., ::-1])  # RGB 2 BGR
        cv2.imwrite(path+imageName, img)

    def binary(self, img):
        result = img.copy()
        (thresh, blackAndWhiteImage) = cv2.threshold(result, 127, 255, cv2.THRESH_BINARY)
        return result

    def detectAruco(self, gray, markerSize=4, totalMarkers=1000, draw=True):
        #  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        key = getattr(cv2.aruco, f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
        arucoDict = cv2.aruco.Dictionary_get(key)
        parameters = cv2.aruco.DetectorParameters_create()
        parameters.minDistanceToBorder = 5
        parameters.cornerRefinementMaxIterations = 149
        parameters.minOtsuStdDev = 4.0
        parameters.adaptiveThreshWinSizeMin = 7
        parameters.adaptiveThreshWinSizeStep = 49
        parameters.minMarkerDistanceRate = 0.014971725679291437
        parameters.maxMarkerPerimeterRate = 10.075976700411534
        parameters.minMarkerPerimeterRate = 0.2524866841549599
        parameters.polygonalApproxAccuracyRate = 0.05562707541937206
        parameters.cornerRefinementWinSize = 9
        parameters.adaptiveThreshConstant = 9.0
        parameters.adaptiveThreshWinSizeMax = 369
        parameters.minCornerDistanceRate = 0.08  # Esse que fez a magica

        (bboxs, ids, rejected) = cv2.aruco.detectMarkers(gray, arucoDict, parameters=parameters)

        markers = []

        if bboxs:
            for bbox, id in zip(bboxs, ids):
                rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                    bboxs, markerSize, self.calibrator.matrix, self.calibrator.distortion)
                # print(rvec, tvec)
                try:
                    rmat = cv2.Rodrigues(rvec)[0]
                    # print(rmat)
                    rotation = self.rotationMatrixToEulerAngles(rmat)
                    markers.append(Marker(bbox, id, rvec, tvec, rmat, rotation))
                except Exception:
                    pass

            if draw:
                cv2.aruco.drawDetectedMarkers(gray, bboxs)

        return markers

    def getMarkerId(self, markers):
        return markers[0].id[0]

    def rotateImage(self, img, markers):
        for marker in markers:
            # print(marker.id[0])

            # cv2.aruco.drawAxis(img, self.calibrator.matrix,
            #                    self.calibrator.distortion, marker.rvec, marker.tvec, 1)
            # print(marker.rotation)
            if abs(marker.rotation[2]) >= 10:
                img = self.rotate_image(img, marker.rotation[2])
            return img

    def rotate_image(self, image, angle):
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
        return result

    def isRotationMatrix(self, R):
        Rt = np.transpose(R)
        shouldBeIdentity = np.dot(Rt, R)
        Id = np.identity(3, dtype=R.dtype)
        n = np.linalg.norm(Id - shouldBeIdentity)
        return n < 1e-6

    def eulerToDegree(self, euler):
        pi = 22.0/7.0
        return ((euler) / (2 * pi)) * 360

    def rotationMatrixToEulerAngles(self, R):

        assert(self.isRotationMatrix(R))

        sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

        singular = sy < 1e-6

        if not singular:
            x = math.atan2(R[2, 1], R[2, 2])
            y = math.atan2(-R[2, 0], sy)
            z = math.atan2(R[1, 0], R[0, 0])
        else:
            x = math.atan2(-R[1, 2], R[1, 1])
            y = math.atan2(-R[2, 0], sy)
            z = 0

        x = self.eulerToDegree(x)
        y = self.eulerToDegree(y)
        z = self.eulerToDegree(z)

        return np.array([x, y, z])

    def detectMarkedCircles(self, img, circles):
        marked_circles = list()
        centroids = list()
        black = None

        if circles is not None and len(circles) != 0:
            for circle in circles[0]:
                (x, y, r) = circle
                x = int(x)
                y = int(y)
                r = int(r)

                result = img[(y-r):(y+(r)), (x-r):(x+(r))]
                colors, count = np.unique(
                    result.reshape(-1, result.shape[-1]), axis=0, return_counts=True)
                if len(count):
                    black = all(i <= 160 for i in list(colors[count.argmax()]))
                    
                    # black = list(colors[count.argmax()]) <= list([150, 150, 150])

                # print(list(colors[count.argmax()]))
                # print(black)

                if black:
                    marked_circles.append(1)
                    centroids.append([x, y])
                else:
                    marked_circles.append(0)
                    centroids.append([x, y])

        return marked_circles, centroids

    def drawCircles(self, img, circles):
        output = img.copy()
        if circles is not None and len(circles) != 0:
            detected_circles = np.uint16(np.around(circles))
            for (x, y, r) in detected_circles[0, :]:
                x = int(x)
                y = int(y)
                r = int(r)
                cv2.circle(output, (x, y), r, (0, 255, 255), 1)
                cv2.circle(output, (x, y), 2, (0, 255, 255), 1)
        return output

    def detectCircles(self, img):
        # grayed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        grayed = img
        blurried = cv2.medianBlur(grayed, 5)
        circles = cv2.HoughCircles(blurried, cv2.HOUGH_GRADIENT, 1, 30,
                                   param1=50, param2=30, minRadius=12, maxRadius=50)

        return circles

    def detectVote(self, marked_circles, centroids):
        y = []
        for centroid in centroids:
            y.append(centroid[1])
        for marked_circle, centroid in zip(marked_circles, centroids):
            if marked_circle == 1:
                if centroid[1] == min(y):
                    return self.vote_labels[0]
                elif centroid[1] == max(y):
                    return self.vote_labels[2]
                else:
                    return self.vote_labels[1]
        return None

    def executeDetectVotes(self, img, draw):

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # gray = self.binary(img)
        # return img,  None,  None, None

        markers = self.detectAruco(img)

        if len(markers) <= 0:
            return gray, None, None, None

        marker_id = self.getMarkerId(markers)
        if marker_id == 0:
            return gray, 0, None,  None

        rotated_image = self.rotateImage(gray, markers)

        circles = self.detectCircles(rotated_image)
        if circles is not None and len(circles[0]) != len(self.vote_labels):
            return rotated_image, None, None, None
        if draw:
            rotated_image = self.drawCircles(rotated_image, circles)

        marked_circles, centroids = self.detectMarkedCircles(rotated_image, circles)

        if marked_circles.count(1) == 0:
            return rotated_image, marker_id, 2, None
        elif marked_circles.count(1) > 1:
            return rotated_image, marker_id, 1, None

        valid_vote = self.detectVote(marked_circles, centroids)

        return rotated_image, marker_id, 0, valid_vote
        #
        # try:
        #     position = (100, 50)
        #     cv2.putText(
        #         return_image,  # numpy array on which text is written
        #         valid_vote,  # text
        #         position,  # position at which writing has to start
        #         cv2.FONT_HERSHEY_SIMPLEX,  # font family
        #         1,  # font size
        #         (0, 255, 0, 255),  # font color
        #         2)  # font stroke
        #
        #     return rotated_image, marker_id, 0, valid_vote
        # except Exception as e:
        #     print(e)
        #     pass
        #
        # return rotated_image, marker_id, 0, valid_vote
