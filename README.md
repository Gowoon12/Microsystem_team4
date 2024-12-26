# Microsystem_team4
This project is part of the wireless system-related code from the 2024 Fall Semester course "Design and Fabrication of Microsystem" at Chonnam National University.

+ Team 4 : Liu Ke, Jeong Gowoon



## System Environment 

+ It was test in Window 10, Arduino IDE 2.3.3, Visual Studio Code, python 3.8.19.

+ The purpose of this project is to fabricate a piezoresistive pressure sensor using MEMS processes, measure its signal, and develop a wireless system to receive the transmitted signal.

+ The detailed system setup is shown in the figure below. 

![System Diagram](SystemSetup.jpg)


![Arduino Setup](SystemSetup2.jpg)

## Prerequirement

+

## Detailed Explanation

+ Please refer to the guides for Installing the [Arduino IDE](https://m.blog.naver.com/bpcode/221994096291) and Setting up [RF Communication](https://m.blog.naver.com/roboholic84/221139363425). (Korean)

+ send.ino and receive.ino are designed to run in the Arduino environment and require a one-time upload to the devices.

+ RealtimePlotting.py is used for real-time plotting of the received data. You can modify this script to include additional features such as custom plotting or pressure calculations.

+ The system includes three example measurements for applied pressures of 0, 50, 100, 150, 200, 250, and 300 kPa with a 1V input.

#### MaxonMotorDLLCarrier.py
  
+ This serves to hold the information of the motor together so that several motors function as Thread.

+ You should change the path to the EPOS library

+ please check your OS and chose the correct .so version.

+ [Here](https://www.maxongroup.com/maxon/view/product/control/Positionierung/EPOS-4/546714), you can download the require software and API. 
  
      path =  '/home/meric/gowoon/MaxonMotor/EPOS4_Linux_Intel_64_Lib/libEposCmd.so.6.6.2.0'
  
- If you are using in the Windows environment, you can use /EPOS4_WinC++_64_Lib/
- If you are using in the Linux environment, you can use /EPOS4_Linux_Intel_64_Lib/libEposCmd.so.6.6.2.0



+ After setting up all hardware systems perfectly, try with

      python Maxon_keyboard.py


