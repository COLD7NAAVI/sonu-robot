#!/usr/bin/env python3
from gpiozero import OutputDevice, PWMOutputDevice
from time import sleep

# === BCM pin mapping ===
# Motor A (left)
A_IN1 = OutputDevice(17)   # forward
A_IN2 = OutputDevice(27)   # backward
A_EN  = PWMOutputDevice(12)

# Motor B (right)
B_IN1 = OutputDevice(22)   # forward
B_IN2 = OutputDevice(23)   # backward
B_EN  = PWMOutputDevice(13)

# === BASIC MOTOR ACTIONS ===

def a_forward(speed=0.9):
    A_IN1.on()
    A_IN2.off()
    A_EN.value = speed

def a_backward(speed=0.9):
    A_IN1.off()
    A_IN2.on()
    A_EN.value = speed

def b_forward(speed=0.9):
    B_IN1.on()
    B_IN2.off()
    B_EN.value = speed

def b_backward(speed=0.9):
    B_IN1.off()
    B_IN2.on()
    B_EN.value = speed

def stop_all():
    A_EN.value = 0
    B_EN.value = 0
    A_IN1.off(); A_IN2.off()
    B_IN1.off(); B_IN2.off()
    sleep(0.05)

# === HIGH-LEVEL MOVEMENT ===

def forward(duration=1.5):
    a_forward(); b_forward()
    print("→ Forward")
    sleep(duration)
    stop_all()

def backward(duration=1.5):
    a_backward(); b_backward()
    print("→ Backward")
    sleep(duration)
    stop_all()

def left(duration=0.7):
    # left wheel backward, right wheel forward
    a_backward(); b_forward()
    print("→ Left Turn")
    sleep(duration)
    stop_all()

def right(duration=0.7):
    # left wheel forward, right wheel backward
    a_forward(); b_backward()
    print("→ Right Turn")
    sleep(duration)
    stop_all()

if __name__ == "__main__":
    try:
        print("Running movement test sequence...")
        forward(1.5)
        sleep(0.5)
        backward(1.5)
        sleep(0.5)
        left(0.8)
        sleep(0.5)
        right(0.8)
        stop_all()
        print("Done.")
    except KeyboardInterrupt:
        stop_all()

