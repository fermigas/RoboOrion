import config
from devices import *
from orion import *
from packets import responsepacket
from testserial import *
import time



t = temperatureSensor(slot.SLOT_2)
#  replace t with ultrasonic distance sensor
#  class ultrasonicSensor(simpledevice, readabledevice):

us = ultrasonicSensor()

testport = testserial()

board = orion(testport)


# board.port1.addDevice(t)

board.port8.addDevice(us)

#testport.write(bytearray([255, 85, 33, 3, 0, 128, 174, 65, 13, 10]))


while True:
    testport.write(bytearray([0xff, 0x55, 0x04, 0x00, 0x01, 001, 0x06]))
    latest = us.latestValue()

    while latest == -1:
        time.sleep(0.5)
        latest = us.latestValue()

    print latest
    latest = -1