# Dynamixel_Linux

+ This is the guide on how to use Robotis Dynamixel motors in a Linux environment using Dynamixel SDK. 

+ The code is written in Python. You can use it on its own or intergrated with ROS(Robot Operating System).

+ If you want to use it in a Windows environment or in other platform, please refer to the explanations [here](https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/overview/). 

+ The code is tested at the ubuntu 18.04, 20.04. 


## [Pre-requirement] Dynamixel Wizard 2.0 

+ Robotiz provide the Dynamixel Wizard 2.0, a GUI software for configuring Dynamixel motors. 

+ You can download the software at the [Robotis website](https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_wizard2/). 

+ If you are using U2D2 and its powerhub, please connect the hardware following the instruction [here](https://emanual.robotis.com/docs/kr/parts/interface/u2d2_power_hub/#%EA%B0%9C%EC%9A%94).

+ When you use more then 1 motor, each motor need to have a same protocol, Baudrate but different ids. 

## Hardware Setup


## Dynamixel SDK Installation

+ You can install the Dynamixel SDK with carefully following the instruction [here](https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/download/#repository). 


## example code 

In the Dynamixel SDK folder, there is some examples for run the motors. 

    cd /DynamixelSDK/python/tests/protocol2_0

read_write.py : control 1 motor
sync_read_write.py : control 2 + motor

For more easier control, the python module is made. 

### motorLLC_sync.py

This code include the functions to control the Dynamixel motor using Dynamixel SDK. 

If you encounter an error stating that Dynamixel SDK cannot be found when running a Python code, you can try resolving it by entering the following command in the terminal.
(from dynamixel_sdk import *)

      pip install dynamixel-sdk


Before you use the code, please check the control table address. Each motor has their own control table address, so please check. 

Example : Assume that you are goint to use 4 motor, 
Only you need to do is..


BAUDRATE = 57600  # Change the boardrate as you set

DEVICENAME = "dev/ttyUSB0"

self.motorN0 = 4

self.IDs = [1, 2, 3, 4] # This will change with your setup by using the Dyanmixel Wizard. 

self.motorType = [2.0, 2.0, 2.0, 2.0] # This means the protocol type. 



 * How to check the Device name?
   
       disconnent the USB port on your computer.
       cd ..
       cd ..
       cd dev
       ls
       Connect the USB port on your computer.
       ls
   
       => One port name will come out and that is the DEVICE NAME

### example.py

+ This is the example code to control the Dynamixel motor. 

+ This include keyboard input control. when you press each keyboard(ASCII code), the motor will move as it defined. ESC key will make it exit. 

+ You can change this code for your system.

Go to the folder include this file, and try 

    python example.py


    
   
