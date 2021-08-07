class QrCodeManager:

    def __init__(self):
        pass

    def generateQrCode(self, data):
        import qrcode
        img = qrcode.make(data)
        img.save('testqr.jpg')

    def readQrCode(self, img):
        import cv2

        detector = cv2.QRCodeDetector()
        data, bbox, straight_qrcode = detector.detectAndDecode(img)

        if bbox is not None:
            n_lines = len(bbox)
            for i in range(n_lines):
                try:
                    point1 = tuple(bbox[i][0])
                    point2 = tuple(bbox[(i+1) % n_lines][0])
                    cv2.line(img, point1, point2, color=(255, 0, 0), thickness=2)
                except Exception:
                    pass

        return data
