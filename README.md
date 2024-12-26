# Microsystem_team4
This project is part of the wireless system-related code from the 2024 Fall Semester course "Design and Fabrication of Microsystem" at Chonnam National University.

Team 4 : Liu Ke, Jeong Gowoon

System Environment 
![System Diagram](SystemSetup.jpg)



# MaxonMotorPython


This is a Python code that allows Mexson motors to be used as CAN communication methods.

It was tested in Ubuntu 20.04 LTS, python 3.8.10. 

[This](https://support.maxongroup.com/hc/en-us/articles/360012695739) can be referred to because the Maxon Motor does not provide applications available in the Linux environment.


## Prerequirement

Before running this code, it must be executed with all hardware setup and EPOS Studio setup completed. 

Don't forget to have the same communication speed and different IDs.

## Setup

/MaxonMotor folder contains basic examples provided by EPOS, including the EPOS library.

/modules folder contains the modules and examples for controlling motors. 

#### MaxonMotorDLLCarrier.py
  
+ This serves to hold the information of the motor together so that several motors function as Thread.

+ You should change the path to the EPOS library

+ please check your OS and chose the correct .so version.

+ [Here](https://www.maxongroup.com/maxon/view/product/control/Positionierung/EPOS-4/546714), you can download the require software and API. 
  
      path =  '/home/meric/gowoon/MaxonMotor/EPOS4_Linux_Intel_64_Lib/libEposCmd.so.6.6.2.0'
  
- If you are using in the Windows environment, you can use /EPOS4_WinC++_64_Lib/
- If you are using in the Linux environment, you can use /EPOS4_Linux_Intel_64_Lib/libEposCmd.so.6.6.2.0

#### MaxonMotorControl.py

+ This is a file that has commands to control the ExxonMotor as a function. You can import the MaxonMotorControlThread class and apply it to your system as needed.

#### Maxon_keyboard.py

+ This is a basic example of controlling a motor with IDs 1, 2, 3, and 4 by keyboard input. Depending on the system, you can change.

## Usage

+ After setting up all hardware systems perfectly, try with

      python Maxon_keyboard.py


