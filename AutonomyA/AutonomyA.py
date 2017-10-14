from config import slot
import logging
from orion import *
import sys
import time
import random 

#   Get basic autonomy program working
#   Build towwards SLAM system until we reach limits
#       computational power
#       sensor sophistocation    
#   Pull code out into libraries as it grows
#   Add sensors and actuators and repeat
#
#   do all that can be done without cameras and lidar
#   start AutonomyB when the limit is reached unless 
#   some natural break occurs earlier

#  we need a reliable and repeatable way to measure success

################
#  issues
#################
#  bumps into things that are too low for the untrasound to catch
#   improvements
#         lower sensor or sensors near the front wheels and back

#  runs over or into things that no sensor can currently catch
#   improvements
#           probably needs camera

#  doesn't have an exploration plan of attack, so can't use historical
#  path to inform where ti will go next  (SLAM)
#       Algorithms for mapping & exploration
#       compass & internal gps
#      

#  gets stuck on the carpet and doesn't retreat sensibly
#   improvements
#       encoders to know if the wheels have slipped
#       landmark checking
#           wifi & bluetooth RSSI triangulation
#           light & color sensors
#           smarter distance sensor array
#           servo-mointed distance sensors
#           sensors pointed at ceiling to get 3d hints

globalSpeed = 100

# Turn on logging
olog = logging.getLogger('orion')
olog.setLevel(logging.INFO)
olog.addHandler(logging.StreamHandler(sys.stdout))

# Create a board
orionBoard = orion()

# Create sensors
us = ultrasonicSensor()
orionBoard.port8.addDevice(us)

# Create actuators
rightMotor = dcmotor()
leftMotor = dcmotor()
orionBoard.motor1.addDevice(rightMotor)
orionBoard.motor2.addDevice(leftMotor)

def forward(speed):
    leftMotor.run(-1*speed)
    rightMotor.run(speed)  

def backward(speed):
    leftMotor.run(speed)
    rightMotor.run(-1*speed)  

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

# with encoders, this might not need to be time-based
def retreatFromObstacle():
        stopWithDelay(0.5)
        backward(globalSpeed)
        time.sleep(0.3)
        stopWithDelay(0.1)

def randomlyturnLeftOrRight():
    if random.randint(1,10) < 6:
        turnLeft(globalSpeed)
    else:
        turnRight(globalSpeed)

lastDistance = us.latestValue()

try:

    while True:
        us.requestValue()
        curDistance = us.latestValue()
        if curDistance != lastDistance:
            print(curDistance)

        forward(globalSpeed) 

        if curDistance < 25.0:
            retreatFromObstacle()
            randomlyturnLeftOrRight()

        time.sleep(0.1)

finally:
    stopWithDelay(0.1)
    orionBoard.__serialPort.close()

