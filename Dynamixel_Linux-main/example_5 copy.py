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
P1 = [4000]
P2 = [3500]
P3 = [3000]
P4 = [2500]
P5 = [2000]
P6 = [1500]
P7 = [1000]
P8 = [500]
P9 = [0]
P10 = [-500]
P11 = [-1000]
P12 = [-1500]
P13 = [-2000]
P14 = [-2500]
P15 = [-3000]
P16 = [-3500]

# P1 = [4000]
# P2 = [3800]
# P3 = [3600]
# P4 = [3400]
# P5 = [3200]
# P6 = [3000]
# P7 = [2800]
# P8 = [2600]
# P9 = [2400]
# P10 = [2200]
# P11 = [2000]
# P12 = [1800]
# P13 = [1600]
# P14 = [1400]
# P15 = [1200]
# P16 = [1000]

# P1 = [4000]
# P2 = [3900]
# P3 = [3800]
# P4 = [3700]
# P5 = [3600]
# P6 = [3500]
# P7 = [3400]
# P8 = [3300]
# P9 = [3200]
# P10 = [3100]
# P11 = [3000]
# P12 = [2900]
# P13 = [2800]
# P14 = [2700]
# P15 = [2600]
# P16 = [2500]

# P1 = [4000]
# P2 = [3950]
# P3 = [3900]
# P4 = [3850]
# P5 = [3800]
# P6 = [3750]
# P7 = [3700]
# P8 = [3650]
# P9 = [3600]
# P10 = [3550]
# P11 = [3500]
# P12 = [3450]
# P13 = [3400]
# P14 = [3350]
# P15 = [3300]
# P16 = [3250]


mc.moveTo(P1)
time.sleep(5)
mc.moveTo(P2)
time.sleep(5)
mc.moveTo(P3)
time.sleep(5)
mc.moveTo(P4)
time.sleep(5)
mc.moveTo(P5)
time.sleep(5)
mc.moveTo(P6)
time.sleep(5)
mc.moveTo(P7)
time.sleep(5)
mc.moveTo(P8)
time.sleep(5)
mc.moveTo(P9)
time.sleep(5)
mc.moveTo(P10)
time.sleep(5)
mc.moveTo(P11)
time.sleep(5)
mc.moveTo(P12)
time.sleep(5)
mc.moveTo(P13)
time.sleep(5)
mc.moveTo(P14)
time.sleep(5)
mc.moveTo(P15)
time.sleep(5)
mc.moveTo(P16)
time.sleep(10)

mc.moveTo(P16)
time.sleep(5)
mc.moveTo(P15)
time.sleep(5)
mc.moveTo(P14)
time.sleep(5)
mc.moveTo(P13)
time.sleep(5)
mc.moveTo(P12)
time.sleep(5)
mc.moveTo(P11)
time.sleep(5)
mc.moveTo(P10)
time.sleep(5)
mc.moveTo(P9)
time.sleep(5)
mc.moveTo(P8)
time.sleep(5)
mc.moveTo(P7)
time.sleep(5)
mc.moveTo(P6)
time.sleep(5)
mc.moveTo(P5)
time.sleep(5)
mc.moveTo(P4)
time.sleep(5)
mc.moveTo(P3)
time.sleep(5)
mc.moveTo(P2)
time.sleep(5)
mc.moveTo(P1)
time.sleep(5)


# Close the motor connection
mc.torque_disable()
mc.close()
