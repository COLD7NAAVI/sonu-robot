# motor_driver.py
from gpiozero import OutputDevice
from time import sleep

AIN1 = OutputDevice(17)
AIN2 = OutputDevice(18)
BIN1 = OutputDevice(22)
BIN2 = OutputDevice(23)

def forward(t=0.5):
    AIN1.on()
    AIN2.off()
    BIN1.on()
    BIN2.off()
    sleep(t)
    stop()

def backward(t=0.5):
    AIN1.off()
    AIN2.on()
    BIN1.off()
    BIN2.on()
    sleep(t)
    stop()

def left(t=0.5):
    AIN1.off()
    AIN2.on()
    BIN1.on()
    BIN2.off()
    sleep(t)
    stop()

def right(t=0.5):
    AIN1.on()
    AIN2.off()
    BIN1.off()
    BIN2.on()
    sleep(t)
    stop()

def stop():
    AIN1.off()
    AIN2.off()
    BIN1.off()
    BIN2.off()
