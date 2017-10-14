from abc import ABCMeta

import config

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
        b = byts[:-2]
        self.valid = True
        self.OkPacket = False
        packetlen = len(b)
        if packetlen < 2 or b[0] != self.PACKETSTART[0] or b[1] != self.PACKETSTART[1]:
            self.valid = False
        if packetlen >= 3:
            self.index = b[2]
        else:
            self.OkPacket = True
            self.index = None
        if packetlen > 3:
            self.datatype = b[3]
            self.data = b[4:]
        else:
            self.datatype = None
            self.data = None

class PacketError(Exception):
    def __init__(self, message):
        super(PacketError, self).__init__(message)
