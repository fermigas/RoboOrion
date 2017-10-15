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
#  path to inform where it will go next  (SLAM)
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

#  start with a calibration phase
#      learn real-world anglualr speed:
#        need to know the speed at which there's an accurate pivot (on different surfaces)
#        turn around a few times in both directions at progressively higher speeds 
#           easiest with a compass 
#           a servo-mounted ultrasound could map distances through an angle, then turn and compare
#               multiple servo-mounted ultrasound sensors might do a really good job
#           try to get back reliably to a given place
#        other cues:  
#           ceiling ir, floor ir, wall ir, photo receptors, color sensors, encoders
#           bluetooth & wireless RSSI, sound
#       
#      learn real-world linear speeds


globalSpeed = 20

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

curDistance = us.latestValue()
while curDistance == -1:
    us.requestValue()
    curDistance = us.latestValue()
    print(time.clock()-start, " priming   " )
    time.sleep(0.1)

try:

    while True:

        if curDistance < 30:
            retreatFromObstacle()
            print(time.clock() - start, "  retreating  ", curDistance)

        while curDistance < 30.0:    # 30 cm           
            turnAwayFromObstacle()
            us.requestValue()
            curDistance = us.latestValue()
            print(time.clock() - start, "  turning  ", curDistance)

        forward(globalSpeed)
        time.sleep(0.05)
        us.requestValue()
        curDistance = us.latestValue()

        print(time.clock() - start, "   forward   ",  curDistance)

except KeyboardInterrupt:
    pass

finally:
    stopWithDelay(0.1)
    orionBoard.closeSerial()    

