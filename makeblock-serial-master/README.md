# makeblock-serial
A set of Python libraries and firmware for easily interfacing with [Makeblock Orion](http://learn.makeblock.cc/orion/) via serial interface. Primarily written for and tested via the [Me Shield for Raspberry Pi](http://learn.makeblock.cc/s4rpi/).

I am relatively new to both Makeblock/Adruino and Raspberry Pi but I've been writing code for a long time. I have been using this project to learn more about both platforms and about Python programming in general. I'm adding support for all of the modules that I have on-hand, as I get the time but if there are particular ones you would like to see sooner than others, just let me know. Open to all comments and suggestions as I am trying to learn as much as I can during this process.

I started from a base of the [RaspberryPiShield](https://github.com/Makeblock-official/RaspberryShield) demo code, specifically the serial demo there. I've been slowly updating the firmware from there to extend and add more devices plus making it work with the latest [Makeblock-libraries](https://github.com/Makeblock-official/Makeblock-Libraries). I have really not spent much time on the firmware side but instead I have been working out the model on the Python side.

## Setup
1) You will first need to push the included firmware to your Orion via the Arduino IDE. Note that this will require that you have the Makeblock libraries setup properly (tested with the v3.22 libraries).

2) Make sure you have unblocked the serial port within the OS on the RPi via the instructions [here]( http://www.irrational.net/2012/04/19/using-the-raspberry-pis-serial-port/)

3) Run the demo.py for a simple example of how to you the Python libraries. You may need to adjust the script for your particular set of sensors and their ports/slots before execution.
