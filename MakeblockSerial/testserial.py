import time

class testserial(object):

    def __init__(self):
        self.__queue = list()

    def write(self, packet):
        self.__queue.append(packet)

    def readline(self):
        while len(self.__queue) == 0:
            time.sleep(0.5)

        return str(self.__queue.pop())
