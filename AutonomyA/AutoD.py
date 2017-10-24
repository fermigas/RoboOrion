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

debugLevel = 'INFO'  # 'DEBUG'
samplingPeriod = 0.005
waitSleep = 0.005
globalSpeed = 20

# Turn on logging
olog = logging.getLogger('orion')

if debugLevel == 'INFO':
    olog.setLevel(logging.INFO)
elif debugLevel == 'DEBUG':
    olog.setLevel(logging.DEBUG)

olog.addHandler(logging.StreamHandler(sys.stdout))

# Create a board
orionBoard = orion()

# Create sensors
us_left = leftUltrasonicSensor()
orionBoard.port8.addDevice(us_left)

us_center = centerUltrasonicSensor()
orionBoard.port3.addDevice(us_center)

us_right = rightUltrasonicSensor()
orionBoard.port4.addDevice(us_right)

# Create actuators
rightMotor = dcmotor()
leftMotor = dcmotor()
orionBoard.motor1.addDevice(rightMotor)
orionBoard.motor2.addDevice(leftMotor)

def forward(speed):
    leftMotor.run(speed)
    rightMotor.run(-1*speed)  

def backward(speed):
    leftMotor.run(-1*speed)
    rightMotor.run(speed)  

def turnLeft(speed):
    leftMotor.run(-1*speed)
    rightMotor.run(-1*speed) 

def turnRight(speed):
    leftMotor.run(speed)
    rightMotor.run(speed)  

def stopWithDelay(delay):
    rightMotor.stop()
    leftMotor.stop()
    time.sleep(delay)

# with encoders, this will not need to be time-based
def retreatFromObstacle(cm = None):
        stopWithDelay(0.5)
        backward(globalSpeed)
        time.sleep(0.3)
        stopWithDelay(0.1)

def turnTowardsDistanceWithFurthestObstacle(leftDistance, rightDistance):
    if leftDistance > rightDistance:
        turnLeft(globalSpeed)
    else:
        turnRight(globalSpeed)
    time.sleep(0.3)
    stopWithDelay(0.1)


def randomlyturnLeftOrRight():
    if random.randint(1,10) < 6:
        turnLeft(globalSpeed)
    else:
        turnRight(globalSpeed)
    time.sleep(0.3)
    stopWithDelay(0.1)

# once we have encoders and a compass we should be able to be more precise about this
def turnAwayFromObstacle(deg = None):   
    randomlyturnLeftOrRight()  # for now we chose a direction randomly

start = time.clock()

leftDistance, leftTime = us_left.latestValueAndTime()
centerDistance, centerTime = us_center.latestValueAndTime()
rightDistance, rightTime = us_right.latestValueAndTime()

while leftDistance == -1 or centerDistance == -1 or rightDistance == -1  :
    us_left.requestValue()
    leftDistance = us_left.latestValue()
    time.sleep(0.1)
    us_center.requestValue()
    centerDistance = us_center.latestValue()
    time.sleep(0.1)
    us_right.requestValue()
    rightDistance = us_right.latestValue()
    time.sleep(0.1)
    print(time.clock()-start, " priming   ", leftDistance, centerDistance, rightDistance )
    time.sleep(0.1)

def pollUntilWeGetANewUltrasoundValue(us_sensor, sensorString):
    distance, millis = us_sensor.latestValueAndTime()
    lastValue = distance
    us_sensor.requestValue()
    counter = 0
    while lastValue == distance and distance != 400.0:
        distance, millis = us_sensor.latestValueAndTime()
        time.sleep(waitSleep)
        log.debug("waiting on " + sensorString + " value" + '  ' +  str(lastValue) + '  ' +   str(distance))
        if counter > 4:
            us_sensor.requestValue()
            counter = 0
        counter = counter + 1
    return distance, millis

def pollUntilWeGetANewUltrasoundTime(us_sensor, sensorString):
    distance, millis = us_sensor.latestValueAndTime()
    lastValue = millis
    us_sensor.requestValue()
    counter = 0
    while lastValue == millis:
        distance, millis = us_sensor.latestValueAndTime()
        time.sleep(waitSleep)
        log.debug("waiting on " + sensorString + " value" + '  ' +  str(lastValue) + '  ' +   str(millis))
        if counter > 4:
            us_sensor.requestValue()
            counter = 0
        counter = counter + 1
    return distance, millis

def getUltrasoundValues():

#    leftDistance, leftMillis = pollUntilWeGetANewUltrasoundValue(us_left, 'left')
#    centerDistance, centerMillis = pollUntilWeGetANewUltrasoundValue(us_center, 'center')
#    rightDistance, rightMillis = pollUntilWeGetANewUltrasoundValue(us_right, 'right')

    leftDistance, leftMillis = pollUntilWeGetANewUltrasoundTime(us_left, 'left')
    centerDistance, centerMillis = pollUntilWeGetANewUltrasoundTime(us_center, 'center')
    rightDistance, rightMillis = pollUntilWeGetANewUltrasoundTime(us_right, 'right')


    return leftDistance, leftMillis, centerDistance, centerMillis, rightDistance, rightMillis

try:

    while True:

        if leftDistance < 30 or centerDistance < 30 or rightDistance < 30 :
            retreatFromObstacle()
            print(time.clock() - start, "  retreating  ", centerDistance, rightDistance, leftDistance )

        while leftDistance < 30 or centerDistance < 30 or rightDistance < 30 :    # 30 cm           
            # turnAwayFromObstacle()
            turnTowardsDistanceWithFurthestObstacle(leftDistance, rightDistance)
            leftDistance, leftMillis, centerDistance, centerMillis, rightDistance, rightMillis = getUltrasoundValues()      
            print(time.clock() - start, "  turning  ", centerDistance, rightDistance, leftDistance)

        forward(globalSpeed)
        time.sleep(samplingPeriod)
        leftDistance, leftMillis, centerDistance, centerMillis, rightDistance, rightMillis = getUltrasoundValues()      
        dataString = ("  %5.4f |  LM: %5.4f L: %5.1f |  CM: %5.4f C: %5.1f |  RM: %5.4f R: %5.1f  " %  
              (time.clock() - start, leftMillis, leftDistance, centerMillis, centerDistance, rightMillis, rightDistance, ))
        print(dataString)
        log.debug('                                                               ' + dataString)

except KeyboardInterrupt:
    pass

finally:
    orionBoard.closeSerial()    


