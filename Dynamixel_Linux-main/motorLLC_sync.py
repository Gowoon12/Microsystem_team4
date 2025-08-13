from dynamixel_sdk import *                    # Uses Dynamixel SDK library

##  ML, MX, MH   #############################
# Control table address
ADDR_PRO_TORQUE_ENABLE      = 64               # Control table address is different in Dynamixel model
ADDR_PRO_GOAL_VEL           = 112
ADDR_PRO_GOAL_POS           = 116
ADDR_PRO_GOAL_POSVEL        = 112

ADDR_PRO_PRESENT_POS        = 132
ADDR_PRO_MOVING             = 122

# Data Byte Length
LEN_PRO_GOAL_POS            = 4
LEN_PRO_GOAL_VEL            = 4
LEN_PRO_GOAL_POSVEL         = 8

LEN_PRO_PRESENT_POS         = 4
LEN_PRO_MOVING              = 1

# Protocol version
PRO_PROTOCOL_VERSION         = 2.0               # See which protocol version is used in the Dynamixel

##  AX, MX   #############################
# Control table address
ADDR_AXMX_TORQUE_ENABLE      = 24               # Control table address is different in Dynamixel model
ADDR_AXMX_GOAL_VEL           = 32
ADDR_AXMX_GOAL_POS           = 30
ADDR_AXMX_GOAL_POSVEL        = 30

ADDR_AXMX_PRESENT_POS        = 36
ADDR_AXMX_MOVING             = 46

# Data Byte Length
LEN_AXMX_GOAL_POS            = 2
LEN_AXMX_GOAL_VEL            = 2
LEN_AXMX_GOAL_POSVEL         = 4

LEN_AXMX_PRESENT_POS         = 2
LEN_AXMX_MOVING              = 1

# Protocol version
AXMX_PROTOCOL_VERSION        = 1.0               # See which protocol version is used in the Dynamixel

# Default setting
BAUDRATE                    = 115200            # Dynamixel default baudrate : 57600  1000000
DEVICENAME                  = "/dev/ttyUSB1"            # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"
TORQUE_ENABLE               = 1                 # Value for enabling the torque
TORQUE_DISABLE              = 0                 # Value for disabling the torque
TYPE_PRO_P2                 = 2.0
TYPE_AXMX_P1                = 1.0

class motorLLC():
    def __init__(self):
        self.motorNo = 1
        self.IDs = [1]
        self.motorType = [2.0]
        self.baudrate = BAUDRATE
        self.device = DEVICENAME

        self.type_PRO_P2_used = False
        self.type_AXMX_P1_used = False

        for ii in range(0, self.motorNo):
            if self.motorType[ii] == TYPE_PRO_P2:
                self.type_PRO_P2_used = True
            if self.motorType[ii] == TYPE_AXMX_P1:
                self.type_AXMX_P1_used = True


    def set_motor_IDs(self, motorNo, IDs, type):
        if (motorNo == len(IDs)) and (motorNo == len(type)):
            self.motorNo = motorNo
            self.IDs = IDs
            self.motorType = type

            self.type_PRO_P2_used = False
            self.type_AXMX_P1_used = False

            for ii in range(0, self.motorNo):
                if self.motorType[ii] == TYPE_PRO_P2:
                    self.type_PRO_P2_used = True
                if self.motorType[ii] == TYPE_AXMX_P1:
                    self.type_AXMX_P1_used = True

        else:
            print("Motor Number is not same")

    def set_baudrate(self, baudrate):
        self.baudrate = baudrate

    def set_devicename(self, devicename):
        self.device = devicename

    def open(self):
        # Initialize PortHandler instance
        self.portHandler = PortHandler(self.device)

        if self.type_AXMX_P1_used:
            # Initialize PacketHandler instance
            self.packetHandlerP1 = PacketHandler(AXMX_PROTOCOL_VERSION)

            self.groupSyncWriteP1_pos = GroupSyncWrite(self.portHandler, self.packetHandlerP1, ADDR_AXMX_GOAL_POS, LEN_AXMX_GOAL_POS)
            self.groupSyncWriteP1_posvel = GroupSyncWrite(self.portHandler, self.packetHandlerP1, ADDR_AXMX_GOAL_POSVEL, LEN_AXMX_GOAL_POSVEL)

            # AX motor cannot use GroupBulkRead function, instead read2ByteTXRX needs to be used.
            #self.groupBulkReadP1_pos = GroupBulkRead(self.portHandler, self.packetHandlerP1)
            #self.groupBulkReadP1_moving = GroupBulkRead(self.portHandler, self.packetHandlerP1)

        if self.type_PRO_P2_used:
            # Initialize PacketHandler instance
            self.packetHandlerP2 = PacketHandler(PRO_PROTOCOL_VERSION)

            self.groupSyncWriteP2_pos = GroupSyncWrite(self.portHandler, self.packetHandlerP2, ADDR_PRO_GOAL_POS, LEN_PRO_GOAL_POS)
            self.groupSyncWriteP2_posvel = GroupSyncWrite(self.portHandler, self.packetHandlerP2, ADDR_PRO_GOAL_POSVEL, LEN_PRO_GOAL_POSVEL)

            self.groupBulkReadP2_pos = GroupBulkRead(self.portHandler, self.packetHandlerP2)
            self.groupBulkReadP2_moving = GroupBulkRead(self.portHandler, self.packetHandlerP2)

        # Add parameter storage for Dynamixel present position value
        for ii in range(0, self.motorNo):
            motorID = self.IDs[ii]
            if self.motorType[ii] == TYPE_PRO_P2:
                dxl_addparam_result = self.groupBulkReadP2_pos.addParam(motorID, ADDR_PRO_PRESENT_POS, LEN_PRO_PRESENT_POS)
                if dxl_addparam_result != True:
                    print("[ID:%03d] groupBulkRead addparam failed_POS" % motorID)
                    quit()
                dxl_addparam_result = self.groupBulkReadP2_moving.addParam(motorID, ADDR_PRO_MOVING, LEN_PRO_MOVING)
                if dxl_addparam_result != True:
                    print("[ID:%03d] groupBulkRead addparam failed_MOVING" % motorID)
                    quit()
            #else:   #if self.motorType[ii] == TYPE_AXMX_P1:
                #dxl_addparam_result = self.groupBulkReadP1_pos.addParam(motorID, ADDR_AXMX_PRESENT_POS, LEN_AXMX_PRESENT_POS)
                #if dxl_addparam_result != True:
                #    print("[ID:%03d] groupBulkRead addparam failed_POS" % motorID)
                #    quit()
                #dxl_addparam_result = self.groupBulkReadP1_moving.addParam(motorID, ADDR_AXMX_MOVING, LEN_AXMX_MOVING)
                #if dxl_addparam_result != True:
                #    print("[ID:%03d] groupBulkRead addparam failed_MOVING" % motorID)
                #    quit()

        # Open port
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            quit()

        # Set port baudrate
        if self.portHandler.setBaudRate(BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            quit()


    def torque_enable(self):
        # Enable Dynamixel#1 Torque
        for ii in range(0, self.motorNo):
            motorID = self.IDs[ii]
            if self.motorType[ii] == TYPE_PRO_P2:
                dxl_comm_result, dxl_error = self.packetHandlerP2.write1ByteTxRx(self.portHandler, motorID, ADDR_PRO_TORQUE_ENABLE, TORQUE_ENABLE)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % self.packetHandlerP2.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % self.packetHandlerP2.getRxPacketError(dxl_error))
                else:
                    print("Dynamixel#%d has been successfully connected" % motorID)
            else:  # if self.motorType[ii] == TYPE_AXMX_P1:
                dxl_comm_result, dxl_error = self.packetHandlerP1.write1ByteTxRx(self.portHandler, motorID, ADDR_AXMX_TORQUE_ENABLE, TORQUE_ENABLE)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % self.packetHandlerP1.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % self.packetHandlerP1.getRxPacketError(dxl_error))
                else:
                    print("Dynamixel#%d has been successfully connected" % motorID)

    def cvtToLongWord(self, pos):
        posi = int(pos)
        return [DXL_LOBYTE(DXL_LOWORD(posi)), DXL_HIBYTE(DXL_LOWORD(posi)), DXL_LOBYTE(DXL_HIWORD(posi)), DXL_HIBYTE(DXL_HIWORD(posi))]

    def cvtToWord(self, pos):
        posi = int(pos)
        return [DXL_LOBYTE(posi), DXL_HIBYTE(posi)]

    def moveTo(self, positions_pulse):
        if self.motorNo != len(positions_pulse):
            print("Motor Number is not same")
            quit()

        # Allocate goal position value into byte array
        dxl_goal_position = []
        for ii in range(0, self.motorNo):
            pos = positions_pulse[ii]
            if self.motorType[ii] == TYPE_PRO_P2:
                dxl_goal_position.append(self.cvtToLongWord(pos))
            else: #if self.motorType[ii] == TYPE_AXMX_P1:
                dxl_goal_position.append(self.cvtToWord(pos))

        # Add Dynamixel#1 goal position value to the Syncwrite parameter storage
        for ii in range(0, self.motorNo):
            motorID = self.IDs[ii]
            if self.motorType[ii] == TYPE_PRO_P2:
                dxl_addparam_result = self.groupSyncWriteP2_pos.addParam(motorID, dxl_goal_position[ii])
                if dxl_addparam_result != True:
                    print("[ID:%03d] groupSyncWriteP2_pos addparam failed" % motorID)
                    quit()
            else:    #if self.motorType[ii] == TYPE_AXMX_P1:
                dxl_addparam_result = self.groupSyncWriteP1_pos.addParam(motorID, dxl_goal_position[ii])
                if dxl_addparam_result != True:
                    print("[ID:%03d] groupSyncWriteP1_pos addparam failed - Ln208" % motorID)
                    quit()


        # Syncwrite goal position
        if self.type_AXMX_P1_used:
            dxl_comm_result = self.groupSyncWriteP1_pos.txPacket()
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandlerP1.getTxRxResult(dxl_comm_result))
            # Clear syncwrite parameter storage
            self.groupSyncWriteP1_pos.clearParam()

        if self.type_PRO_P2_used:
            dxl_comm_result = self.groupSyncWriteP2_pos.txPacket()
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandlerP2.getTxRxResult(dxl_comm_result))
            # Clear syncwrite parameter storage
            self.groupSyncWriteP2_pos.clearParam()

    def moveTo_wVel_pps(self, positions_pulse, velocities_pps):
        pulse_per_rotation = 4096.0
        unit_of_rpm = 0.229
        min_to_sec = 60.0

        coeff_pps_to_dxlrpm = min_to_sec/pulse_per_rotation/unit_of_rpm

        vel_rpm = []
        for ii in range(0, len(velocities_pps)):
            vel_rpm.append(velocities_pps[ii]*coeff_pps_to_dxlrpm)

        self.moveTo_wVel_rpm(positions_pulse, vel_rpm)

    # the unit of velocity (dxlrpm) is 0.229 rev/min.
    def moveTo_wVel_rpm(self, positions_pulse, velocities_dxlrpm):
        if self.motorNo != len(positions_pulse):
            print("Motor Number is not same as length of positions")
            quit()

        if self.motorNo != len(velocities_dxlrpm):
            print("Motor Number is not same as length of velocities")
            quit()

        # Allocate goal position value into byte array
        dxl_goalP2_velpos = []
        dxl_goalP1_posvel = []
        for ii in range(0, self.motorNo):
            if self.motorType[ii] == TYPE_PRO_P2:
                if abs(velocities_dxlrpm[ii])<10:
                    if velocities_dxlrpm[ii] < 0:
                        velpos = self.cvtToLongWord(-10)
                    else:
                        velpos = self.cvtToLongWord(10)
                else:
                    velpos = self.cvtToLongWord(velocities_dxlrpm[ii])
                velpos.extend(self.cvtToLongWord(positions_pulse[ii]))
                dxl_goalP2_velpos.append(velpos)

            else:   #if self.motorType[ii] == TYPE_AXMX_P1:
                posvel = self.cvtToWord(positions_pulse[ii])
                if abs(velocities_dxlrpm[ii]) < 10:
                    if velocities_dxlrpm[ii] < 0:
                        posvel.extend(self.cvtToWord(-10))
                    else:
                        posvel.extend(self.cvtToWord(10))
                else:
                    posvel.extend(self.cvtToWord(velocities_dxlrpm[ii]))
                dxl_goalP1_posvel.append(posvel)

        # Add Dynamixel's goal position value to the Syncwrite parameter storage
        ii_P1 = 0
        ii_P2 = 0
        for ii in range(0, self.motorNo):
            motorID = self.IDs[ii]
            if self.motorType[ii] == TYPE_PRO_P2:
                dxl_addparam_result = self.groupSyncWriteP2_posvel.addParam(motorID, dxl_goalP2_velpos[ii_P2])
                ii_P2 += 1
                if dxl_addparam_result != True:
                    print("[ID:%03d] groupSyncWriteP2_posvel addparam failed" % motorID)
                    quit()
            else:   #if self.motorType[ii] == TYPE_AXMX_P1:
                dxl_addparam_result = self.groupSyncWriteP1_posvel.addParam(motorID, dxl_goalP1_posvel[ii_P1])
                ii_P1 += 1
                if dxl_addparam_result != True:
                    print("[ID:%03d] groupSyncWriteP1_posvel addparam failed" % motorID)
                    quit()

        if self.type_PRO_P2_used:
            # Syncwrite goal position
            dxl_comm_result = self.groupSyncWriteP2_posvel.txPacket()
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandlerP2.getTxRxResult(dxl_comm_result))
            # Clear syncwrite parameter storage
            self.groupSyncWriteP2_posvel.clearParam()

        if self.type_AXMX_P1_used:
            # Syncwrite goal position
            dxl_comm_result = self.groupSyncWriteP1_posvel.txPacket()
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandlerP1.getTxRxResult(dxl_comm_result))
            # Clear syncwrite parameter storage
            self.groupSyncWriteP1_posvel.clearParam()

    def read_position(self):
        dxl_present_position = []

        if self.type_PRO_P2_used:
            dxl_comm_result = self.groupBulkReadP2_pos.txRxPacket()
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandlerP2.getTxRxResult(dxl_comm_result))

            for ii in range(0, self.motorNo):
                motorID = self.IDs[ii]
                if self.motorType[ii] == TYPE_PRO_P2:
                    dxl_getdata_result = self.groupBulkReadP2_pos.isAvailable(motorID, ADDR_PRO_PRESENT_POS, LEN_PRO_PRESENT_POS)
                    if dxl_getdata_result:
                        pos = self.groupBulkReadP2_pos.getData(motorID, ADDR_PRO_PRESENT_POS, LEN_PRO_PRESENT_POS)
                        dxl_present_position.append(pos)

        if self.type_AXMX_P1_used:
            for ii in range(0, self.motorNo):
                motorID = self.IDs[ii]
                if self.motorType[ii] == TYPE_AXMX_P1:
                    pos, dxl_comm_result, dxl_error = self.packetHandlerP1.read2ByteTxRx(self.portHandler, motorID, ADDR_AXMX_PRESENT_POS)
                    if dxl_comm_result != COMM_SUCCESS:
                        print("%s" % self.packetHandlerP1.getTxRxResult(dxl_comm_result))
                    elif dxl_error != 0:
                        print("%s" % self.packetHandlerP1.getRxPacketError(dxl_error))
                    else:
                        dxl_present_position.append(pos)
                        
        return dxl_present_position


    def readMoving(self):
        # Syncread present position
        if self.type_AXMX_P1_used:
            dxl_comm_result = self.groupBulkReadP1_moving.txRxPacket()
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandlerP1.getTxRxResult(dxl_comm_result))

        if self.type_PRO_P2_used:
            dxl_comm_result = self.groupBulkReadP2_moving.txRxPacket()
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandlerP2.getTxRxResult(dxl_comm_result))


        dxl_moving_status = []
        for ii in range(0, self.motorNo):
            motorID = self.IDs[ii]
            if self.motorType[ii] == TYPE_PRO_P2:
                # Check if groupbulkread data of Dynamixel is available
                dxl_getdata_result = self.groupBulkReadP2_moving.isAvailable(motorID, ADDR_PRO_MOVING, LEN_PRO_MOVING)
                if dxl_getdata_result != True:
                    print("[ID:%03d] groupSyncRead getdata failed - Ln366" % motorID)
                    quit()
                # Get Dynamixel present position value

                dxl_moving_status.append(self.groupBulkReadP2_pos.getData(motorID, ADDR_PRO_MOVING, LEN_PRO_MOVING))
            else:  #  if self.motorType[ii] is TYPE_AXMX_P1:
                moving_status, dxl_comm_result, dxl_error = self.packetHandlerP1.read1ByteTxRx(self.portHandler, motorID,
                                                                                                ADDR_AXMX_MOVING)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % self.packetHandlerP1.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % self.packetHandlerP1.getRxPacketError(dxl_error))
                dxl_moving_status.append(moving_status)
            #    # Check if groupbulkread data of Dynamixel is available
            #    dxl_getdata_result = self.groupBulkReadP1_moving.isAvailable(motorID, ADDR_AXMX_MOVING, LEN_AXMX_MOVING)
            #    if dxl_getdata_result != True:
            #        print("[ID:%03d] groupSyncRead getdata failed - Ln375" % motorID)
            #        quit()
                # Get Dynamixel present position value

            #    dxl_moving_status.append(self.groupBulkReadP1_pos.getData(motorID, ADDR_AXMX_MOVING, LEN_AXMX_MOVING))

        return dxl_moving_status

    def close(self):
        # Clear syncread parameter storage
        #if self.type_AXMX_P1_used:
        #    self.groupBulkReadP1_pos.clearParam()
        #    self.groupBulkReadP1_moving.clearParam()
        if self.type_PRO_P2_used:
            self.groupBulkReadP2_pos.clearParam()
            self.groupBulkReadP2_moving.clearParam()

        # Disable Dynamixel#1 Torque
        for ii in range(0, self.motorNo):
            motorID = self.IDs[ii]
            if self.motorType[ii] == TYPE_PRO_P2:
                dxl_comm_result, dxl_error = self.packetHandlerP2.write1ByteTxRx(self.portHandler, motorID, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % self.packetHandlerP2.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % self.packetHandlerP2.getRxPacketError(dxl_error))
            else:  #if self.motorType[ii] == TYPE_AXMX_P1:
                dxl_comm_result, dxl_error = self.packetHandlerP1.write1ByteTxRx(self.portHandler, motorID, ADDR_AXMX_TORQUE_ENABLE, TORQUE_DISABLE)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % self.packetHandlerP1.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % self.packetHandlerP1.getRxPacketError(dxl_error))

        # Close port
        self.portHandler.closePort()
