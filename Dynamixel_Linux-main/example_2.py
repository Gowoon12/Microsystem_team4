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
pos_1 = [2820]
pos_2 = [2800]

beating = 1  # Start counting from 1

print("Press 'esc' to quit the program.")
 
while True:
    # Perform movement and beat counting
    mc.moveTo(pos_1)
    time.sleep(0.02)  # Wait for 1 second

    mc.moveTo(pos_2)
    
    # Print the beating count
    print(f"{beating} beating")
    beating += 1  # Increment the beat count
    
    time.sleep(1)  # Wait for 1 second

    # # Check if the 'esc' key is pressed to break the loop and exit
    # if getch() == chr(0x1b):  # esc key
    #     print("Exiting loop...")
    #     break

# Close the motor connection
mc.torque_disable()
mc.close()
