/*************************************************************************
* File Name          : RoboOrion.ino
* Author             : Ander, Mark Yan
* Updated            : Teets, Jon,  Ander, Mark Yan
* Version            : V0a.01.106
* Date               : 01/03/2017
* Description        : Refactoring of orion_firmware.ino -- Firmware for Makeblock Electronic modules with Scratch.
* License            : CC-BY-SA 3.0
* Copyright (C) 2013 - 2016 Maker Works Technology Co., Ltd. All right reserved.
* http://www.makeblock.cc/
**************************************************************************/


#include <Wire.h>
#include <SoftwareSerial.h>
#include <Arduino.h>
#include <MeOrion.h>

Servo servos[8];
MeDCMotor dc;
MeUltrasonicSensor us;
MePort generalDevice;
MeInfraredReceiver *ir = NULL;
MeBuzzer buzzer;
Me4Button buttonSensor;


union {
	byte byteVal[4];
	float floatVal;
	long longVal;
}val;

union {
	byte byteVal[8];
	double doubleVal;
}valDouble;

union {
	byte byteVal[2];
	short shortVal;
}valShort;


typedef struct MeModule
{
	int device;
	int port;
	int slot;
	int pin;
	int index;
	float values[3];
} MeModule;

MeModule modules[12];


int analogs[8] = { A0,A1,A2,A3,A4,A5,A6,A7 };


String mVersion = "0a.01.106";

boolean isAvailable = false;
boolean isBluetooth = false;

int len = 52;
char buffer[52];
char bufferBt[52];
byte index = 0;
byte dataLen;
byte modulesLen = 0;
boolean isStart = false;
unsigned char irRead;
char serialRead;
unsigned char prevc = 0;


#define VERSION 0
#define ULTRASONIC_SENSOR 1

#define MOTOR 10
#define SERVO 11
#define IR 13
#define IRREMOTE 14

#define INFRARED 16
#define LINEFOLLOWER 17
#define IRREMOTECODE 18

#define LIMITSWITCH 21
#define BUTTON 22

#define DIGITAL 30
#define ANALOG 31
#define PWM 32
#define SERVO_PIN 33
#define TONE 34
#define PULSEIN 37
#define ULTRASONIC_ARDUINO 36

#define TIMER 50

#define GET 1
#define RUN 2
#define RESET 4
#define START 5

float angleServo = 90.0;
int servo_pins[8] = { 0,0,0,0,0,0,0,0 };
double lastTime = 0.0;
double currentTime = 0.0;
uint8_t keyPressed = 0;
uint8_t command_index = 0;


void readSerial() {
	isAvailable = false;
	if (Serial.available()>0) {
		isAvailable = true;
		isBluetooth = false;
		serialRead = Serial.read();
	}
}


void writeSerial(unsigned char c) {
	Serial.write(c);
}


void setup() {
	pinMode(13, OUTPUT);
	digitalWrite(13, HIGH);
	delay(300);
	digitalWrite(13, LOW);
	Serial.begin(115200);
	delay(500);
	buzzerOn();
	delay(100);
	buzzerOff();

// 	Serial1.begin(115200);

	Serial.print("Version: ");
	Serial.println(mVersion);
}




void loop() {

	keyPressed = buttonSensor.pressed();

	currentTime = millis() / 1000.0 - lastTime;

	if (ir != NULL)
		ir->loop();

	readSerial();

	if (isAvailable) {

		unsigned char c = serialRead & 0xff;

		if (c == 0x55 && isStart == false) {
			if (prevc == 0xff) {
				index = 1;
				isStart = true;
			}
		}
		else {
			prevc = c;
			if (isStart) {
				if (index == 2) {
					dataLen = c;
				}
				else if (index>2) {
					dataLen--;
				}
				writeBuffer(index, c);
			}
		}
		index++;
		if (index>51) {
			index = 0;
			isStart = false;
		}
		if (isStart&&dataLen == 0 && index>3) {
			isStart = false;
			parseData();
			index = 0;
		}
	}
}

unsigned char readBuffer(int index) {
	return isBluetooth ? bufferBt[index] : buffer[index];
}

void writeBuffer(int index, unsigned char c) {
	if (isBluetooth) {
		bufferBt[index] = c;
	}
	else {
		buffer[index] = c;
	}
}
void writeHead() {
	writeSerial(0xff);
	writeSerial(0x55);
}
void writeEnd() {
	Serial.println();
}



void callOK() {
	writeSerial(0xff);
	writeSerial(0x55);
	writeEnd();
}

/*
ff 55 len idx action device port  slot  data a
0  1  2   3   4      5      6     7     8
*/
void parseData() {
	isStart = false;
	int idx = readBuffer(3);
	command_index = (uint8_t)idx;
	int action = readBuffer(4);
	int device = readBuffer(5);

	switch (action) {
		case GET: 
			if (device != ULTRASONIC_SENSOR) {
				writeHead();
				writeSerial(idx);
			}
			readSensor(device);
			writeEnd();
			break;

		case RUN: 
			runModule(device);
			callOK();
			break;

		case RESET: 
			dc.reset(M1);
			dc.run(0);
			dc.reset(M2);
			dc.run(0);
			dc.reset(PORT_1);
			dc.run(0);
			dc.reset(PORT_2);
			dc.run(0);
			callOK();	
			break;

		case START: 
			callOK();
			break;
	}

}

void sendByte(char c) {
	writeSerial(1);
	writeSerial(c);
}
void sendString(String s) {
	int l = s.length();
	writeSerial(4);
	writeSerial(l);
	for (int i = 0; i<l; i++) {
		writeSerial(s.charAt(i));
	}
}
void sendFloat(float value) {
	writeSerial(0x2);
	val.floatVal = value;
	writeSerial(val.byteVal[0]);
	writeSerial(val.byteVal[1]);
	writeSerial(val.byteVal[2]);
	writeSerial(val.byteVal[3]);
}
void sendShort(double value) {
	writeSerial(3);
	valShort.shortVal = value;
	writeSerial(valShort.byteVal[0]);
	writeSerial(valShort.byteVal[1]);
}
void sendDouble(double value) {
	writeSerial(2);
	valDouble.doubleVal = value;
	writeSerial(valDouble.byteVal[0]);
	writeSerial(valDouble.byteVal[1]);
	writeSerial(valDouble.byteVal[2]);
	writeSerial(valDouble.byteVal[3]);
}
short readShort(int idx) {
	valShort.byteVal[0] = readBuffer(idx);
	valShort.byteVal[1] = readBuffer(idx + 1);
	return valShort.shortVal;
}
float readFloat(int idx) {
	val.byteVal[0] = readBuffer(idx);
	val.byteVal[1] = readBuffer(idx + 1);
	val.byteVal[2] = readBuffer(idx + 2);
	val.byteVal[3] = readBuffer(idx + 3);
	return val.floatVal;
}
long readLong(int idx) {
	val.byteVal[0] = readBuffer(idx);
	val.byteVal[1] = readBuffer(idx + 1);
	val.byteVal[2] = readBuffer(idx + 2);
	val.byteVal[3] = readBuffer(idx + 3);
	return val.longVal;
}
void runModule(int device) {
	//0xff 0x55 0x6 0x0 0x1 0xa 0x9 0x0 0x0 0xa
	int port = readBuffer(6);
	int pin = port;
	switch (device) {
	case MOTOR: {
		int speed = readShort(7);
		dc.reset(port);
		dc.run(speed);
	}
				break;

	case SERVO: {
		int slot = readBuffer(7);
		pin = slot == 1 ? mePort[port].s1 : mePort[port].s2;
		int v = readBuffer(8);
		Servo sv = servos[searchServoPin(pin)];
		if (v >= 0 && v <= 180)
		{
			if (!sv.attached())
			{
				sv.attach(pin);
			}
			sv.write(v);
		}
	}
				break;
	case DIGITAL: {
		pinMode(pin, OUTPUT);
		int v = readBuffer(7);
		digitalWrite(pin, v);
	}
				  break;
	case PWM: {
		pinMode(pin, OUTPUT);
		int v = readBuffer(7);
		analogWrite(pin, v);
	}
			  break;
	case TONE: {
		pinMode(pin, OUTPUT);
		int hz = readShort(7);
		int ms = readShort(9);
		if (ms>0) {
			buzzer.tone(pin, hz, ms);
		}
		else {
			buzzer.noTone(pin);
		}
	}
			   break;
	case SERVO_PIN: {
		int v = readBuffer(7);
		Servo sv = servos[searchServoPin(pin)];
		if (v >= 0 && v <= 180)
		{
			if (!sv.attached())
			{
				sv.attach(pin);
			}
			sv.write(v);
		}
	}
					break;
	case TIMER: {
		lastTime = millis() / 1000.0;
	}
				break;
	}
}

int searchServoPin(int pin) {
	for (int i = 0; i<8; i++) {
		if (servo_pins[i] == pin) {
			return i;
		}
		if (servo_pins[i] == 0) {
			servo_pins[i] = pin;
			return i;
		}
	}
	return 0;
}
void readSensor(int device) {
	/**************************************************
	ff 55 len idx action device port slot data a
	0  1  2   3   4      5      6    7    8
	***************************************************/
	float value = 0.0;
	int port, slot, pin;
	port = readBuffer(6);
	pin = port;
	switch (device) {
	case  ULTRASONIC_SENSOR: {
		if (us.getPort() != port) {
			us.reset(port);
		}
		value = us.distanceCm();
		writeHead();
		writeSerial(command_index);
		sendFloat(value);
	}
							 break;
	case  INFRARED:
	{
		if (ir == NULL)
		{
			ir = new MeInfraredReceiver(port);
			ir->begin();
		}
		else if (ir->getPort() != port)
		{
			delete ir;
			ir = new MeInfraredReceiver(port);
			ir->begin();
		}
		irRead = ir->getCode();
		if ((irRead < 255) && (irRead > 0))
		{
			sendFloat((float)irRead);
		}
		else
		{
			sendFloat(0);
		}
	}
	break;
	case  LINEFOLLOWER: {
		if (generalDevice.getPort() != port) {
			generalDevice.reset(port);
			pinMode(generalDevice.pin1(), INPUT);
			pinMode(generalDevice.pin2(), INPUT);
		}
		value = generalDevice.dRead1() * 2 + generalDevice.dRead2();
		sendFloat(value);
	}
						break;
	case LIMITSWITCH: {
		slot = readBuffer(7);
		if (generalDevice.getPort() != port || generalDevice.getSlot() != slot) {
			generalDevice.reset(port, slot);
		}
		if (slot == 1) {
			pinMode(generalDevice.pin1(), INPUT_PULLUP);
			value = !generalDevice.dRead1();
		}
		else {
			pinMode(generalDevice.pin2(), INPUT_PULLUP);
			value = !generalDevice.dRead2();
		}
		sendFloat(value);
	}
					  break;
	case  VERSION: {
		sendString(mVersion);
	}
				   break;
	case  DIGITAL: {
		pinMode(pin, INPUT);
		sendFloat(digitalRead(pin));
	}
				   break;
	case  ANALOG: {
		pin = analogs[pin];
		pinMode(pin, INPUT);
		sendFloat(analogRead(pin));
	}
				  break;
	case  PULSEIN: {
		int pw = readShort(7);
		pinMode(pin, INPUT);
		sendShort(pulseIn(pin, HIGH, pw));
	}
				   break;
	case ULTRASONIC_ARDUINO: {
		int trig = readBuffer(6);
		int echo = readBuffer(7);
		pinMode(trig, OUTPUT);
		digitalWrite(trig, LOW);
		delayMicroseconds(2);
		digitalWrite(trig, HIGH);
		delayMicroseconds(10);
		digitalWrite(trig, LOW);
		pinMode(echo, INPUT);
		sendFloat(pulseIn(echo, HIGH, 30000) / 58.0);
	}
							 break;
	case TIMER: {
		sendFloat((float)currentTime);
	}
				break;
	case BUTTON:
	{
		if (buttonSensor.getPort() != port) {
			buttonSensor.reset(port);
		}
		sendByte(keyPressed == readBuffer(7));
	}
	break;
	}
}