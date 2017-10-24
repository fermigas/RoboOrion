from abc import ABCMeta
import logging
import config


log = logging.getLogger("orion")


class serialpacket():

    __metaclass__ = ABCMeta

    PACKETSTART = [255, 85]

class requestpacket(serialpacket):
    
    def __init__(self, index, action, device, port, slot = None, data = None):
        self.index = index
        self.action = config.action.validate(action)
        self.device = config.device.validate(device)
        self.port = config.port.validate(port)
        if slot != None:
            self.slot = config.slot.validate(slot)
        else:
            self.slot = None
        self.data = data

    def toByteArray(self):
        length = 4
        if self.slot != None or self.data != None:
            length = length + 1
            if self.data != None:
                length = length + len(self.data)
        b = bytearray()
        b.extend(serialpacket.PACKETSTART)
        b.append(length)
        b.append(self.index)
        b.append(self.action)
        b.append(self.device)
        b.append(self.port)
        if self.slot != None:
            b.append(self.slot)
        elif self.data != None:
            b.append(0)
        if self.data != None:
            b.extend(self.data)

        return b
        


class responsepacket(serialpacket):

    def __init__(self, byts):

        byteStream = byts[:-2]   #  grab all but the eol characters
        self.valid = True
        self.OkPacket = False
        self.hasMillis = False

        if len(byteStream) < 2 or  byteStream[0] != self.PACKETSTART[0] or  byteStream[1] != self.PACKETSTART[1]:
            self.valid = False
            return

        if len(byteStream) >= 3:   #  doWeHaveData(len(byteStream)):  
            self.index = byteStream[2]  # if so, the third character is the command_index (port)
        else:
            self.OkPacket = True  # if not, it's just an acknowledgement packet
            self.index = None

        payloadLength = len(byteStream) - 2   # header is 2 bytes
        log.debug(" payloadLength:  " + str(payloadLength) )

        if payloadLength == 0:
            self.datatype = None
            self.data = None
        elif payloadLength == 11 :  # value for ultrasound and the time  
            self.datatype = byteStream[3]
            self.data = byteStream[4:8]
            self.millis = byteStream[-4:]
            self.hasMillis = True
        else:
            self.datatype = byteStream[3]
            self.data = byteStream[4:8]

    def preambleIsRight(byteStream):
        if  byteStream[0] != self.PACKETSTART[0] or  byteStream[1] != self.PACKETSTART[1]:
            return False
        return True



class PacketError(Exception):
    def __init__(self, message):
        super(PacketError, self).__init__(message)
