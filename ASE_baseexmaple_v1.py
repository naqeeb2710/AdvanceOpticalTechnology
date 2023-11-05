# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 15:42:17 2023

@author: dingl
"""

import os
import time
import numpy as np
import matplotlib.pyplot as plt


from seabreeze.spectrometers import list_devices, Spectrometer
from pylablib.devices import Thorlabs



#%%
ans=Thorlabs.list_kinesis_devices()
#ans=pll.list_backend_resources("serial")
stage = Thorlabs.KinesisMotor(ans[0][0])
stage.get_device_info()
devices = list_devices()
print(devices)
spec = Spectrometer(devices[0])
#%%

#First need to home the filter wheel
#must increase the speed otherwise it takes forever
stage.setup_homing(velocity=500000)
stage.home()
stage.wait_move()


#%%
#space for spectrometer setup parameters
spec.integration_time_micros(1e5)
#%% acquisition
#need to change this if the laser spot is at different location on the filter wheel
fig = plt.figure()
ax = fig.add_subplot(111)
wavelengths = spec.wavelengths()
intensities= spec.intensities()
ax.plot(wavelengths,intensities)
#plott, = ax.plot(wavelengths,intensities)
stage.move_to(0)
locations = np.linspace(0,-5000000,num=3)
for mm in range(len(locations)):
    stage.move_to(locations[mm])
    stage.wait_move()
    time.sleep(0.5)
    #careful the backlash from the motor, need settling time
    wavelengths = spec.wavelengths()
    intensities= spec.intensities()    
    #plott.set_xdata(wavelengths)
    #plott.set_ydata(intensities)
    ax.plot(wavelengths,intensities)
    fig.canvas.draw()
    fig.canvas.flush_events()
    time.sleep(1.0)
    #needs some work if want to see the graph before the next step goes
