import time
import numpy as np
from pylablib.devices import Thorlabs

Thorlabs.list_kinesis_devices()
# ans=Thorlabs.KinesisMotor()
# print(ans)
# stage = Thorlabs.KinesisMotor(ans[0][0])
stage = Thorlabs.KinesisMotor("55357574")

print(stage.get_position)
stage.setup_velocity(7329109)
stage.move_to(136533*90)
stage.wait_move()
stage.close()

Thorlabs.list_kinesis_devices()
ans=Thorlabs.list_kinesis_devices()
# print(ans)
stage = Thorlabs.KinesisMotor(ans[0][0])
# stage = Thorlabs.KinesisMotor("55357574")


time.sleep(1)
stage.setup_homing(velocity=7329109)
stage.home()
stage.wait_move()
print(stage.get_position)
stage.wait_move()
time.sleep(1)
stage.is_homed()
stage.is_opened()
stage.close()

