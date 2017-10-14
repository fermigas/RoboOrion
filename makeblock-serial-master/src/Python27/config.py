import exceptions
from types import *

class validatable:

    @classmethod
    def validate(cls, item):
        for memberName in dir(cls):
            member = getattr(cls, memberName)
            if type(member) == IntType and item == member:
                return item
        raise ConfigError("Invalid " + str(cls.__name__) + ": " + str(item))

class action(validatable):

    GET = 1
    RUN = 2
    RESET = 3
    START = 4

class device(validatable):
    
    VERSION = 0
    ULTRASONIC_SENSOR = 1
    TEMPERATURE_SENSOR = 2
    LIGHT_SENSOR = 3
    POTENTIONMETER = 4
    JOYSTICK = 5
    GYRO = 6
    SOUND_SENSOR = 7
    RGBLED = 8
    SEVSEG = 9
    MOTOR = 10
    SERVO = 11
    ENCODER = 12
    IR = 13
    PIRMOTION = 15
    INFRARED = 16
    LINEFOLLOWER = 17
    SHUTTER = 20
    LIMITSWITCH = 21
    BUTTON = 22
    DIGITAL = 30
    ANALOG = 31
    PWM = 32
    SERVO_PIN = 33
    TOUCH_SENSOR = 34
    STEPPER = 40
    ENCODER = 41
    TIMER = 50

class port(validatable):

    PORT_1 = 1
    PORT_2 = 2
    PORT_3 = 3
    PORT_4 = 4
    PORT_5 = 5
    PORT_6 = 6
    PORT_7 = 7
    PORT_8 = 8
    MOTOR_1 = 9
    MOTOR_2 = 10

class slot(validatable):

    SLOT_1 = 1
    SLOT_2 = 2

class ConfigError(Exception):
    def __init__(self, message):
        super(ConfigError, self).__init__(message)