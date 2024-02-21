import time
import os
import sys
from ctypes import *

if sys.version_info < (3, 8):
    os.chdir(r"C:\Program Files\Thorlabs\Kinesis")
else:
    os.add_dll_directory(r"C:\Program Files\Thorlabs\Kinesis")

lib: CDLL = cdll.LoadLibrary("Thorlabs.MotionControl.KCube.DCServo.dll")

    # Uncomment this line if you are using simulations
    #lib.TLI_InitializeSimulations()

    # Set constants
serial_num = c_char_p(b"55357574")

STEPS_PER_REV = c_double(136533)  # for the K10CR1
gbox_ratio = c_double(1.0)  # gearbox ratio
pitch = c_double(1.0)
lib.CC_SetMoveAbsolutePosition(serial_num, c_double(0.0))

# Apply these values to the device
lib.CC_SetMotorParamsExt(serial_num, STEPS_PER_REV, gbox_ratio, pitch)

# Open the Device to move to zero and set it home
if lib.TLI_BuildDeviceList() == 0:
        lib.CC_Open(serial_num)
        lib.CC_StartPolling(serial_num, c_int(200))

        lib.CC_MoveToPosition(serial_num,0)
        lib.CC_SetHomingVelocity(serial_num,7329109*50)
        vel=lib.CC_GetHomingVelocity(serial_num)
        time.sleep(0.25)
        print("Homing",vel)
        lib.CC_Home(serial_num)
        time.sleep(0.25)

        # Close the device
        lib.CC_StopPolling(serial_num)
        lib.CC_Close(serial_num)

time.sleep(0.5)
# Open the Device to move to position
if lib.TLI_BuildDeviceList() == 0:
        lib.CC_Open(serial_num)
        lib.CC_StartPolling(serial_num, c_int(200))
        
        # v=lib.CC_GetVelParamsBlock(serial_num)
        lib.CC_MoveToPosition(serial_num,50*136533)
        lib.CC_SetHomingVelocity(serial_num,7329109*25)
        print(lib.CC_RequestPosition(serial_num))
        time.sleep(0.1)
        print(lib.CC_GetPosition(serial_num))
        print(c_int(lib.CC_GetPosition(serial_num)))
        lib.CC_Home(serial_num)
        time.sleep(0.5)

        # lib.CC_MoveAbsolute(serial_num)
        # lib.CC_Home(serial_num)

        # Close the device
        lib.CC_Close(serial_num)

time.sleep(1.0)

### JOG MOVE
if lib.TLI_BuildDeviceList() == 0:
        lib.CC_Open(serial_num)
        lib.CC_StartPolling(serial_num, c_int(200))
        lib.CC_ClearMessageQueue(serial_num)

        print("Moving to 40 steps")
        lib.CC_MoveRelative(serial_num, 40*136533)  #JOG MOVE
        lib.CC_SetHomingVelocity(serial_num,7329109*50)
        lib.CC_RequestPosition(serial_num)
        

        lib.CC_StopPolling(serial_num)

        time.sleep(0.25)

        lib.CC_Close(serial_num)
    

    

    


