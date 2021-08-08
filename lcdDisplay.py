from subprocess import Popen, PIPE
from time import sleep
from datetime import datetime
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd


class LCDDisplay():

    def __init__(self):

        
        # Modify this if you have a different sized character LCD
        self.columns = 16
        self.rows = 2

        # compatible with all versions of RPI as of Jan. 2019
        # v1 - v3B+
        self.regSel = digitalio.DigitalInOut(board.D16)
        self.enable = digitalio.DigitalInOut(board.D20)
        self.d4 = digitalio.DigitalInOut(board.D8)
        self.d5 = digitalio.DigitalInOut(board.D1)
        self.d6 = digitalio.DigitalInOut(board.D7)
        self.d7 = digitalio.DigitalInOut(board.D12)


        # Initialise the lcd class
        self.lcd = characterlcd.Character_LCD_Mono(self.regSel, self.enable, self.d4, self.d5, self.d6,
                                            self.d7, self.columns, self.rows)

    
        # wipe LCD screen before we start
        self.lcd.clear()
        
        sleep(2)
        '''
        # date and time
        lcd_line_1 = datetime.now().strftime('%b %d  %H:%M:%S\n')

        # current ip address
        lcd_line_2 = "ELECTION PIPA"

        # combine both lines into one update to the display
        self.writeInfo(lcd_line_1, lcd_line_2)
        # self.lcd.message = lcd_line_1 + lcd_line_2
        '''

    def writeInfo(self, line1, line2):
        
        self.lcd.clear()
        self.lcd.message = line1 + '\n' + line2



