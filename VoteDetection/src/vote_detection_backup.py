import cv2
import numpy as np


IMAGES_PATH = '/home/rafh/git/local/DetectCircle/images/'


class ColorFixer:
    HSV_RANGES = {
        # red is a major color
        'red': [
            {
                'lower': np.array([0, 39, 64]),
                'upper': np.array([20, 255, 255])
            },
            {
                'lower': np.array([161, 39, 64]),
                'upper': np.array([180, 255, 255])
            }
        ],
        # yellow is a minor color
        'yellow': [
            {
                'lower': np.array([21, 39, 64]),
                'upper': np.array([40, 255, 255])
            }
        ],
        # green is a major color
        'green': [
            {
                'lower': np.array([41, 39, 64]),
                'upper': np.array([80, 255, 255])
            }
        ],
        # cyan is a minor color
        'cyan': [
            {
                'lower': np.array([81, 39, 64]),
                'upper': np.array([100, 255, 255])
            }
        ],
        # blue is a major color
        'blue': [
            {
                'lower': np.array([101, 39, 64]),
                'upper': np.array([140, 255, 255])
            }
        ],
        # violet is a minor color
        'violet': [
            {
                'lower': np.array([141, 39, 64]),
                'upper': np.array([160, 255, 255])
            }
        ],
        # next are the monochrome ranges
        # black is all H & S values, but only the lower 25% of V
        'black': [
            {
                'lower': np.array([0, 0, 0]),
                'upper': np.array([180, 255, 63])
            }
        ],
        # gray is all H values, lower 15% of S, & between 26-89% of V
        'gray': [
            {
                'lower': np.array([0, 0, 64]),
                'upper': np.array([180, 38, 228])
            }
        ],
        # white is all H values, lower 15% of S, & upper 10% of V
        'white': [
            {
                'lower': np.array([0, 0, 229]),
                'upper': np.array([180, 38, 255])
            }
        ]
    }

    def __init__(self):
        pass

    def createMask(self, hsv_img, colors):

        mask = np.zeros((hsv_img.shape[0], hsv_img.shape[1]), dtype=np.uint8)

        for color in colors:
            for color_range in self.HSV_RANGES[color]:
                mask += cv2.inRange(
                    hsv_img,
                    color_range['lower'],
                    color_range['upper']
                )

        return mask


class VoteDetector:

    color_fixer = ColorFixer()
    vote_labels = []

    def __init__(self, vote_labels):
        self.vote_labels = vote_labels

    def saveimg(self, path, imageName, img, convert=False):
        if convert:
            img = np.copy(img[..., ::-1])  # RGB 2 BGR
        cv2.imwrite(path+imageName, img)

    # def detectBar(self, img, onlyCenter=False):
    #     img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    #
    #     red_mask = self.color_fixer.createMask(img_hsv, ['red'])
    #
    #     mask_img = cv2.bitwise_and(img_hsv, img_hsv, mask=red_mask)
    #     return mask_img
    #     lines = cv2.HoughLinesP(mask_img, 1, (3.14 / 360), 50, 50, 10)
    #
    #     if lines is not None and len(lines) and len(lines[0]) == 1:
    #         if onlyCenter:
    #             centroid = int((lines[0][0][0]+lines[0][0][2]) /
    #                            2), int((lines[0][0][1]+lines[0][0][3])/2)
    #             return centroid
    #
    #         for line in lines[0]:
    #             centroid = int((line[0]+line[2])/2), int((line[1]+line[3])/2)
    #             cv2.circle(mask_img, centroid, 1, (0, 255, 0), 8)
    #             pt1 = (line[0], line[1])
    #             pt2 = (line[2], line[3])
    #             cv2.line(mask_img, pt1, pt2, (255, 255, 255), 2)
    #
    #     return img_hsv

    def detectBar(self, img, onlyCenter=False):
        # primeiro converter para hsv CV_BGR2HSV
        hsvImage = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # fazer split dos hsvChannels
        hsvChannels = cv2.split(hsvImage)

        # hue = 0 para vermelho
        # huerange = 15
        hueValue = 0
        hueRange = 15

        # minsaturation =50
        # minvalue = 50
        minSaturation = 50
        minValue = 50

        # hueimage vai ser hsvchannels[0]
        hueImage = hsvChannels[0]
        hueMask = cv2.inRange(hueImage, hueValue - hueRange, hueValue + hueRange)

        if (hueValue - hueRange < 0 or hueValue + hueRange > 180):
            upperHueValue = hueValue + 180
            hueMaskUpper = cv2.inRange(hueImage, upperHueValue - hueRange,
                                       upperHueValue + hueRange)
            hueMask = hueMask | hueMaskUpper

        saturationMask = hsvChannels[1] > minSaturation
        valueMask = hsvChannels[2] > minValue
        hueMask = (hueMask & saturationMask) & valueMask
        result = cv2.bitwise_and(img, img, mask=hueMask)
        lines = cv2.HoughLinesP(hueMask, 1, (3.14 / 360), 50, 50, 10)

        if lines is not None and len(lines) and len(lines[0]) == 1:
            if onlyCenter:
                centroid = int((lines[0][0][0]+lines[0][0][2]) /
                               2), int((lines[0][0][1]+lines[0][0][3])/2)
                return centroid

            for line in lines[0]:
                centroid = int((line[0]+line[2])/2), int((line[1]+line[3])/2)
                cv2.circle(result, centroid, 1, (0, 255, 0), 8)
                pt1 = (line[0], line[1])
                pt2 = (line[2], line[3])
                cv2.line(result, pt1, pt2, (255, 255, 255), 2)

        return result

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
                    black = list(colors[count.argmax()]) <= list([150, 150, 150])

                if black:
                    marked_circles.append(1)
                    centroids.append([x, y])
                else:
                    marked_circles.append(0)
                    centroids.append([x, y])

        return marked_circles, centroids

    def calcAndSort(self, bar, centroids):
        permutation = None

        bar = np.array(bar)
        centroids = np.array(centroids)

        if bar.ndim == 1:
            dist = np.linalg.norm(centroids - bar, ord=2, axis=1)
            permutation = np.argsort(dist)
        return permutation

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
        grayed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurried = cv2.medianBlur(grayed, 5)
        circles = cv2.HoughCircles(blurried, cv2.HOUGH_GRADIENT, 1, 30,
                                   param1=50, param2=30, minRadius=30, maxRadius=50)

        return circles

    def executeDetectVotes(self, img, draw=False):
        circles = self.detectCircles(img)

        if circles is not None:
            print('Numero de circulos: ', len(circles))

        if circles is not None and len(circles[0]) != len(self.vote_labels):
            return img, None

        return_image = img.copy()
        if draw:
            return_image = self.drawCircles(img, circles)
        marked_circles, centroids = self.detectMarkedCircles(img, circles)

        if marked_circles.count(1) != 1:
            return return_image, None

        bar_center = self.detectBar(img, onlyCenter=True)
        permutation = self.calcAndSort(bar_center, centroids)
        votes = np.array(self.vote_labels)

        if permutation is not None and len(permutation):
            marked_circles = np.array(marked_circles)
            marked_circles = marked_circles[permutation]
            vote_index = np.where(marked_circles == 1)

            try:

                # position = (100, 50)
                # cv2.putText(
                #     return_image,  # numpy array on which text is written
                #     votes[vote_index][0],  # text
                #     position,  # position at which writing has to start
                #     cv2.FONT_HERSHEY_SIMPLEX,  # font family
                #     1,  # font size
                #     (0, 255, 0, 255),  # font color
                #     2)  # font stroke

                return return_image, list(votes[vote_index])
            except Exception as e:
                print(e)
                pass

        return return_image, None
