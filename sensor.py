import win32com.client
import time


class Sensor:
    diffuser: int = 1  # diffuser (0, ('N/A',))
    measurement_mode: int = 1  # MeasMode (1, ('Power', 'Energy'))
    pulse_length: int = 0 # PulseLengths (0, ('30uS', '1.0mS'))
    measurement_range: int = 3 #Ranges (2, ('20.0uJ', '2.00uJ', '200nJ', '20.0nJ'))
    wavelength: int = 3  #Wavelengths (1, ('640', '400', '355', '532', '905', '1064'))

    def __init__(self):
        self.OphirCOM = None
        self.DeviceHandle = None
        self.connected: bool = False
        self.ready: bool = False
        self.armed: bool = False
        self.is_plasma: bool = False
        self.shotn: int = 0
    
    def set_measurement_range(self, measurement_range):
        self.measurement_range = measurement_range

    def status(self) -> int:
        if not self.connected:
            return -1
        if self.armed:
            return 1
        if not self.ready:
            return 2
        return 0

    def connect(self):
        self.connected = False
        self.ready = False
        self.armed = False
        self.OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
        # Stop & Close all devices
        self.OphirCOM.StopAllStreams()
        self.OphirCOM.CloseAll()
        # Scan for connected Devices
        DeviceList = self.OphirCOM.ScanUSB()
        if len(DeviceList) == 0:
            return False
        Device = DeviceList[0]
        self.DeviceHandle = self.OphirCOM.OpenUSBDevice(Device)  # open first device
        exists = self.OphirCOM.IsSensorExists(self.DeviceHandle, 0)
        if exists:
            self.OphirCOM.SetMeasurementMode(self.DeviceHandle, 0, self.measurement_mode)
            self.OphirCOM.SetPulseLength(self.DeviceHandle, 0, self.pulse_length)
            self.OphirCOM.SetRange(self.DeviceHandle, 0, self.measurement_range)
            self.OphirCOM.SetWavelength(self.DeviceHandle, 0, self.wavelength)
            self.connected = True
            self.ready = True
            print('Ophir connect OK')
            return True

    def arm(self, is_plasma=False, shotn=0,delay_seconds=0.05):
        self.is_plasma = is_plasma
        self.shotn = shotn
        if self.connected and self.ready:
            exists = self.OphirCOM.IsSensorExists(self.DeviceHandle, 0)
            if exists:
                self.OphirCOM.StartStream(self.DeviceHandle, 0)  # start measuring
                time.sleep(delay_seconds)
                self.ready = False
                self.armed = True
                #print('Armed OK')
                return True
            print('Not exists!')
        else:
            print('Sensor is not connected!')
        return False

    def disarm(self) -> float:
        if self.connected and self.armed:
            exists = self.OphirCOM.IsSensorExists(self.DeviceHandle, 0)
            if exists:
                self.ready = False
                self.armed = False
                data = self.OphirCOM.GetData(self.DeviceHandle, 0)
                self.OphirCOM.StopStream(self.DeviceHandle, 0)
                events: list[(float, float, float)] = []
                total_power = 0.0  # Initialize total power
                num_events = 0  # Initialize number of events

                for i in range(0, len(data[0]), 2):
                    if i>=60 :
                        events.append((data[1][i] - data[1][0], data[0][i], data[2][i]))
                        total_power += data[0][i]  # Accumulate power for each event
                        num_events += 1

                average_power = total_power / num_events
                print(f"Number of Events: {num_events}", average_power)
                average_power_nanojoules = average_power * 1e9
                print(f"Average Power: {average_power_nanojoules:.2f} nanojoules")
                self.ready = True

                return events, average_power_nanojoules
            print('Not exists!')
        else:
            print('Sensor is not connected!')
        return 0.0


    def __del__(self):
        if self.OphirCOM is not None:
            self.OphirCOM.StopAllStreams()
            self.OphirCOM.CloseAll()
            self.OphirCOM = None

# Function to test the sensor
# def main():
#     import time
    
#     # Create an instance of the Sensor class
#     Start_time = time.time()
#     sensor = Sensor()
    
#     # Connect to the sensor
#     if sensor.connect():
#         print("Sensor connected successfully.")
        
#         # Arm the sensor
#         if sensor.arm():
#             print("Sensor armed successfully.")
            
#             # Disarm the sensor and get events
#             events = sensor.disarm()
#             if events:
#                 print("Events recorded:")
#                 with open('dump.csv', 'w') as dump:
#                     # Write header
#                     dump.write('time, power, status\n')
                    
#                     # Write data rows
#                     for event in events:
#                         dump.write('%.3f, %.2e, %.2f\n' % (event[0], event[1], event[2]))

#                 print('File written')

#             else:
#                 print("No events recorded.")
#         else:
#             print("Failed to arm the sensor.")
#     else:
#         print("Failed to connect to the sensor.")
    
#     # Print the total time taken
#     print(f"Total time: {time.time() - Start_time}s")

# if __name__ == "__main__":
#     main()

