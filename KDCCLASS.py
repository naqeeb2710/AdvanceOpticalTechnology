import time
import os
import sys
from ctypes import *

class ThorlabsMotionController:
    def __init__(self):
        self.lib = None
        self.serial_num = c_char_p(b"55357574")
        self.STEPS_PER_REV = c_double(136533)  # for the K10CR1
        self.gbox_ratio = c_double(1.0)  # gearbox ratio
        self.pitch = c_double(1.0)
        self.dll_path = r"C:\Program Files\Thorlabs\Kinesis"

        if sys.version_info < (3, 8):
            os.chdir(self.dll_path)
        else:
            os.add_dll_directory(self.dll_path)

        self.lib = cdll.LoadLibrary("Thorlabs.MotionControl.KCube.DCServo.dll")

    def open_device(self):
        if self.lib.TLI_BuildDeviceList() == 0:
            self.lib.CC_Open(self.serial_num)
            self.lib.CC_StartPolling(self.serial_num, c_int(200))

    def close_device(self):
        self.lib.CC_StopPolling(self.serial_num)
        self.lib.CC_Close(self.serial_num)

    def move_home(self):
        self.open_device()
        self.lib.CC_MoveToPosition(self.serial_num, 0)
        self.lib.CC_SetHomingVelocity(self.serial_num, 7329109 * 50)
        time.sleep(0.25)
        self.lib.CC_Home(self.serial_num)
        time.sleep(0.25)
        self.close_device()

    def move_to_angle(self, angle):
        self.open_device()
        steps = int(angle * self.STEPS_PER_REV.value)
        self.lib.CC_MoveToPosition(self.serial_num, steps)
        self.lib.CC_SetHomingVelocity(self.serial_num, 7329109 * 25)
        self.lib.CC_RequestPosition(self.serial_num)
        time.sleep(0.1)
        print("Current position:", self.lib.CC_GetPosition(self.serial_num)/self.STEPS_PER_REV.value)
        self.lib.CC_Home(self.serial_num)
        time.sleep(0.5)
        self.close_device()

    def jog_move(self, steps):
        self.open_device()
        self.lib.CC_ClearMessageQueue(self.serial_num)
        print("Moving by {} steps".format(steps))
        self.lib.CC_MoveRelative(self.serial_num, int(steps * self.STEPS_PER_REV.value))
        self.lib.CC_SetHomingVelocity(self.serial_num, 7329109 * 50)
        self.lib.CC_RequestPosition(self.serial_num)
        time.sleep(0.1)
        print("Current position:", self.lib.CC_GetPosition((self.serial_num)/self.STEPS_PER_REV.value))
        self.close_device()

# Example usage:
controller = ThorlabsMotionController()
controller.move_home()

