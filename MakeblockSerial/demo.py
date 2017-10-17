from config import slot
import logging
from orion import *
import sys
import time

# Turn on logging
olog = logging.getLogger('orion')
olog.setLevel(logging.INFO)
olog.addHandler(logging.StreamHandler(sys.stdout))

# Create a board
orionBoard = orion()

# Create some sensors to plug into the board
tempSensor = temperatureSensor(slot.SLOT_1)
sevSeg = sevenSegmentDisplay()

# Add sensors to the ports they are connected to
orionBoard.port4.addDevice(tempSensor)
orionBoard.port3.addDevice(sevSeg)

# Read the most recent temperature from the temp
# sensor and display
lastTemp = tempSensor.latestValue()
while True:
    tempSensor.requestValue()

    curTemp = tempSensor.latestValue()
    if curTemp != lastTemp:
        sevSeg.setValue(curTemp)

    time.sleep(0.5)