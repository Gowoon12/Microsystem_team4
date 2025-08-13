import os
from motorLLC_sync import *
from dynamixel_sdk import * 
import time  # Make sure to import time for sleep

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

mc = motorLLC()
mc.open()
mc.torque_enable()

# The positions you want to move the motor to
pos_1_1 = [0]
pos_1_2 = [2048]
pos_2 = [4095]
pos_2 = [4095]

while True:
    beating = 1  # Start counting from 1

    for _ in range(10):
        # Perform movement and beat counting
        mc.moveTo(pos_1_1)
        time.sleep(1)  # Wait for 1 second
        mc.moveTo(pos_2)
        
        # Print the beating count
        print(f"[Case 1] {beating} beating")
        beating += 1  # Increment the beat count
        
        time.sleep(3)  # Wait for 1 second

    beating = 1  # Start counting from 1

    for _ in range(10):
        # Perform movement and beat counting
        mc.moveTo(pos_1_2)
        time.sleep(0.5)  # Wait for 1 second
        mc.moveTo(pos_2)
        
        # Print the beating count
        print(f"[Case 2] {beating} beating")
        beating += 1  # Increment the beat count
        
        time.sleep(3)  # Wait for 1 second

    beating = 1  # Start counting from 1

    for _ in range(10):
        # Perform movement and beat counting
        mc.moveTo(pos_1_1)
        time.sleep(0.5)  # Wait for 1 second
        mc.moveTo(pos_2)
        
        # Print the beating count
        print(f"[Case 3] {beating} beating")
        beating += 1  # Increment the beat count
        
        time.sleep(3)  # Wait for 1 second
        
    beating = 1  # Start counting from 1

    for _ in range(10):
        # Perform movement and beat counting
        mc.moveTo(pos_1_2)
        time.sleep(0.5)  # Wait for 1 second
        mc.moveTo(pos_2)
        
        # Print the beating count
        print(f"[Case 4] {beating} beating")
        beating += 1  # Increment the beat count
        
        time.sleep(3)  # Wait for 1 second

    time.sleep(5)

# Close the motor connection
mc.torque_disable()
mc.close()
