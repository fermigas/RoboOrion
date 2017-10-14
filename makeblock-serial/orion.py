from abc import ABCMeta
import config
from devices import *
import exceptions
import logging
from packets import responsepacket
import serial
import threading
import sys

log = logging.getLogger("orion")

class serialReader(threading.Thread):
        
    def __init__(self, serialPort, dataHandler):
        threading.Thread.__init__(self)
        self.dataHandler = dataHandler
        self.serialPort = serialPort
    
    def run(self):
        while True:
            line = self.serialPort.readline()
            lineMap = map(ord, line)
            log.debug('Data received: ' + str(lineMap))
            self.dataHandler(lineMap)

class board():
    __metaclass__ = ABCMeta

    @staticmethod
    def __unpackIndex(byte):
        return (byte & 15, byte >> 4 & 15)

    def __init__(self, ports, serialPort = None):

        self.__ports = ports

        # check whether we are running on windows, mac or a linux flavor and chose the correct serial port
        # this is mainly to avoid having to comment/uncomment each time we move between platforms
        # we should probably get more fancy about this in the future: 
        #       1) moving this to the caller or check to see of we have an orionfirmware out there to control
        #       2) supporting bluetooth

        whichPort = ''
        if sys.platform == 'win32':   # works on 64-bit systems, too, at least on python27
            whichPort = 'COM11'
        elif sys.platform == 'linux2':  # Raspberry or linux box  
            whichPort = '/dev/ttyUSB0'
        elif sys.platform == 'darwin':  # Mac 
            whichPort = '/dev/ttyUSB0'

        try:
            self.__serialPort = serialPort or serial.Serial(whichPort, 115200)
        except serial.serialutil.SerialException:
            log.error(whichPort + '  is in use')

        
        log.info("Begin serial port read")
        th = serialReader(self.__serialPort, self.handleResponse)
        th.setDaemon(True)
        th.start()

    def handleResponse(self, byts):
        response = responsepacket(byts)
        # skip invalid packets
        if not response.valid:
            log.debug('Skipping invalid packet')
            return

        if response.OkPacket:
            log.debug('Received OK packet')
            return

        (portNumber, slotNumber) = board.__unpackIndex(response.index)
        responsePort = self.__ports[portNumber]
        if responsePort.occupied:
            log.debug('Sending packet to port %s, slot %s' % (str(portNumber), str(slotNumber)))
            responsePort.getDevice(slotNumber).parseData(response.data)
        else:
            log.error('No handler found for data at port %s, slot %s' % (str(portNumber), str(slotNumber)))

    def sendRequest(self, requestPacket):
        self.__serialPort.write(requestPacket.toByteArray())

class orion(board):
    
    def __init__(self, serialPort = None):
        self.port1 = port(self, config.port.PORT_1)
        self.port2 = port(self, config.port.PORT_2)
        self.port3 = port(self, config.port.PORT_3)
        self.port4 = port(self, config.port.PORT_4)
        self.port5 = port(self, config.port.PORT_5)
        self.port6 = port(self, config.port.PORT_6)
        self.port7 = port(self, config.port.PORT_7)
        self.port8 = port(self, config.port.PORT_8)
        self.motor1 = port(self, config.port.MOTOR_1)
        self.motor2 = port(self, config.port.MOTOR_2)
        ports = {
                    config.port.PORT_1 : self.port1,
                    config.port.PORT_2 : self.port2,
                    config.port.PORT_3 : self.port3,
                    config.port.PORT_4 : self.port4,
                    config.port.PORT_5 : self.port5,
                    config.port.PORT_6 : self.port6,
                    config.port.PORT_7 : self.port7,
                    config.port.PORT_8 : self.port8,
                    config.port.MOTOR_1 : self.motor1,
                    config.port.MOTOR_2 : self.motor2,
                }

        super(orion, self).__init__(ports, serialPort)

class port(object):
    
    def __init__(self, board, portNumber):
        self.__board = board
        self.id = config.port.validate(portNumber)
        self.__occupied = False
        self.__devices = []

    @property
    def occupied(self):
        return self.__occupied

    def addDevice(self, device):
        log.info('%s added to port %s' % (type(device).__name__, str(self.id)))
        self.__occupied = True

        if not hasattr(device, "slot") and len(self.__devices) > 0:
            raise BoardError("Port %s is already occupied" % str(self.id))

        if hasattr(device, "slot") and device.slot != None:
            if len(self.__devices) >= 2:
                raise BoardError("Port %s is already occupied" % str(self.id))
            for d in self.__devices:
                if d.slot == device.slot:
                    raise BoardError("Port %s, slot %s is already occupied" % (str(self.id), device.slot))

        self.__devices.append(device)

        device.port = self
        device.index = device.port.id
        if hasattr(device, "slot") and device.slot != None:
            device.index = device.index + (device.slot << 4)

    def getDevice(self, slot = None):
        if slot == None or slot == 0:
            return self.__devices[0]
        for d in self.__devices:
            if d.slot == slot:
                return d

    def sendRequest(self, requestPacket):
        log.debug('Sending request for port ' + str(self.id))
        self.__board.sendRequest(requestPacket)

class BoardError(Exception):
    def __init__(self, message):
        super(BoardError, self).__init__(message)