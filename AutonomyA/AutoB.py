#  AutoB.py
#  Essentially AutonomyA with no movement
#  This is just for testing sensors
#  start it running and put Spokey in different configurations 
#  It will emit time-based measurements to a file

#  TODO:
#  Add millis to orion_firmware data which is returned


import logging
import time
import random 
import sys




if sys.platform == 'win32':   # works on 64-bit systems, too, at least on python27
    sys.path.append('/Users/jon/Dropbox/robots/Orion/RoboOrion')
elif sys.platform == 'linux2':  # Raspberry or linux box  
    sys.path.append('/home/jon/robotics/RoboOrion')
elif sys.platform == 'darwin':  # Mac 
    sys.path.append('/Users/jonteets/robotics/RoboOrion')


from MakeblockSerial.config import slot
from MakeblockSerial.orion import *


samplingPeriod = 0.3

# Turn on logging
olog = logging.getLogger('orion')
# olog.setLevel(logging.INFO)
olog.setLevel(logging.DEBUG)
olog.addHandler(logging.StreamHandler(sys.stdout))

# Create a board
orionBoard = orion()

# Create sensors
us_center = centerUltrasonicSensor()
orionBoard.port3.addDevice(us_center)

us_right = rightUltrasonicSensor()
orionBoard.port4.addDevice(us_right)

us_left = leftUltrasonicSensor()
orionBoard.port8.addDevice(us_left)


start = time.clock()

centerDistance = us_center.latestValue()
rightDistance = us_right.latestValue()
leftDistance = us_left.latestValue()

while centerDistance == -1 or rightDistance == -1 or leftDistance == -1 :
    us_center.requestValue()
    centerDistance = us_center.latestValue()
    time.sleep(0.1)
    us_right.requestValue()
    rightDistance = us_right.latestValue()
    time.sleep(0.1)
    us_left.requestValue()
    leftDistance = us_left.latestValue()
    time.sleep(0.1)
    print(time.clock()-start, " priming   ",  centerDistance, rightDistance, leftDistance )
    time.sleep(0.1)

def getUltrasoundValues():

    lastValue = centerDistance = us_center.latestValue()
    us_center.requestValue()
    counter = 0
    while lastValue == centerDistance and centerDistance != 400.0:
        centerDistance = us_center.latestValue()
        time.sleep(0.05)
        log.debug("waiting on center value" + '  ' +  str(lastValue) + '  ' +   str(centerDistance))
        #  put a counter here;  after 5 tries, poll for another value
        if counter > 4:
            us_center.requestValue()
        counter = counter + 1


    lastValue = rightDistance = us_right.latestValue()
    us_right.requestValue()
    counter = 0
    while lastValue == rightDistance and rightDistance != 400.0:
        rightDistance = us_right.latestValue()
        time.sleep(0.05)
        log.debug("waiting on right value" + '  ' +   str(lastValue) + '  ' +   str(rightDistance))
        if counter > 4:
            us_right.requestValue()
        counter = counter + 1


    lastValue = leftDistance = us_left.latestValue()
    us_left.requestValue()
    counter = 0
    while lastValue == leftDistance and leftDistance != 400.0:
        leftDistance = us_left.latestValue()
        time.sleep(0.05)
        log.debug("waiting on left value" + '  ' +   str(lastValue) + '  ' +  str( leftDistance))
        if counter > 4:
            us_left.requestValue()
        counter = counter + 1

    return centerDistance, rightDistance, leftDistance

try:

    while True:

        time.sleep(samplingPeriod)
        centerDistance, rightDistance, leftDistance = getUltrasoundValues()      
        dataString = ("  %5.4f   C: %5.1f  R: %5.1f  L: %5.1f" %  
              (time.clock() - start, centerDistance, rightDistance, leftDistance))
        print(dataString)
        log.debug('                                                               ' + dataString)

except KeyboardInterrupt:
    pass

finally:
    orionBoard.closeSerial()    


