import numpy as np
import cv2 as cv
import glob


class CameraCalibrator:

    IMAGES_PATH = '/home/rafh/git/utfpr/raspController/VoteDetection/chess_images/*.jpg'
    matrix = None
    distortion = None

    def __init__(self):
        pass

    def calibrate(self):
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((6*7, 3), np.float32)
        objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)
        # Arrays to store object points and image points from all the images.
        objpoints = []  # 3d point in real world space
        imgpoints = []  # 2d points in image plane.
        images = glob.glob(self.IMAGES_PATH)
        for fname in images:
            img = cv.imread(fname)
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            # Find the chess board corners
            ret, corners = cv.findChessboardCorners(gray, (7, 6), None)
            # If found, add object points, image points (after refining them)
            if ret:
                objpoints.append(objp)
                corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                imgpoints.append(corners)
                # Draw and display the corners
                cv.drawChessboardCorners(img, (7, 6), corners2, ret)
                ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(
                    objpoints, imgpoints, gray.shape[::-1], None, None)
                self.matrix = mtx
                self.distortion = dist
                self.rvecs = np.array(rvecs)
                self.tvecs = np.array(tvecs)


# calibrator = CameraCalibrator()
# calibrator.calibrate()
# print(calibrator.matrix)
# print(calibrator.distortion)
