"""
PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""

import tempfile
from pyfingerprint.pyfingerprint import PyFingerprint


class FingerprintSensor():


    def __init__(self):

        ## Tries to initialize the sensor
        try:
            self.f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

            if (self.f.verifyPassword() == False ):
                raise ValueError('The given fingerprint sensor password is wrong!')

        except Exception as e:
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
            exit(1)

    def getFinger(self):


        ## Tries to read image and download it
        try:
            print('Put your finger in there...')

            ## Wait that finger is read
            while (self.f.readImage() == False ):
                pass

            print('Downloading image (this take a while)...')

            imageDestination =  tempfile.gettempdir() + '/fingerprint.bmp'
            self.f.downloadImage(imageDestination)

            print('The image was saved to "' + imageDestination + '".')

        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            exit(1)

    def searchFinger(self):
        
        ## Tries to search the finger and calculate hash
        try:
            print('Waiting for finger...')

            ## Wait that finger is read
            while (self.f.readImage() == False ):
                pass

            ## Converts read image to characteristics and stores it in charbuffer 1
            self.f.convertImage(0x01)

            ## Searchs template
            result = self.f.searchTemplate()

            self.positionNumber = result[0]
            accuracyScore = result[1]

            if (self.positionNumber == -1 ):
                print('No match found!')
            else:
                print('Found template at position #' + str(self.positionNumber))
                print('The accuracy score is: ' + str(accuracyScore))

            # ## Loads the found template to charbuffer 1
            # self.f.loadTemplate(self.positionNumber, 0x01)

            # ## Downloads the characteristics of template loaded in charbuffer 1
            # characterics = str(self.f.downloadCharacteristics(0x01)).encode('utf-8')

            # ## Hashes characteristics of template
            # print('SHA-2 hash of template: ' + hashlib.sha256(characterics).hexdigest())

        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            return -1
            # exit(1)
        
        return result[0]
