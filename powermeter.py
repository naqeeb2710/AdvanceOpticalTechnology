import win32com.client


class Sensor:
    diffuser: int = 1  # diffuser (0, ('N/A',))
    measurement_mode: int = 1  # MeasMode (1, ('Power', 'Energy'))
    pulse_length: int = 0 # PulseLengths (0, ('30uS', '1.0mS'))
    measurement_range: int = 2  #Ranges (2, ('10.0J', '2.00J', '200mJ', '20.0mJ', '2.00mJ', '200uJ'))
    wavelength: int = 3  #Wavelengths (3, (' 193', ' 248', ' 532', '1064', '2100', '2940'))

    def __init__(self):
        self.OphirCOM = None
        self.DeviceHandle = None
        self.connected: bool = False
        self.ready: bool = False
        self.armed: bool = False
        self.is_plasma: bool = False
        self.shotn: int = 0

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
            print('diffuser', self.OphirCOM.GetDiffuser(self.DeviceHandle, 0))
            print('MeasMode', self.OphirCOM.GetMeasurementMode(self.DeviceHandle, 0))
            print('PulseLengths', self.OphirCOM.GetPulseLengths(self.DeviceHandle, 0))
            print('Ranges', self.OphirCOM.GetRanges(self.DeviceHandle, 0))
            print('Wavelengths', self.OphirCOM.GetWavelengths(self.DeviceHandle, 0))

            #self.OphirCOM.StopStream(self.DeviceHandle, 0)
            #self.OphirCOM.SetDiffuser(self.DeviceHandle, 0, self.diffuser)
            self.OphirCOM.SetMeasurementMode(self.DeviceHandle, 0, self.measurement_mode)
            self.OphirCOM.SetPulseLength(self.DeviceHandle, 0, self.pulse_length)
            self.OphirCOM.SetRange(self.DeviceHandle, 0, self.measurement_range)
            self.OphirCOM.SetWavelength(self.DeviceHandle, 0, self.wavelength)
            self.connected = True
            self.ready = True
            print('Ophir connect OK')
            return True

    def arm(self, is_plasma=False, shotn=0):
        self.is_plasma = is_plasma
        self.shotn = shotn
        if self.connected and self.ready:
            exists = self.OphirCOM.IsSensorExists(self.DeviceHandle, 0)
            if exists:
                self.OphirCOM.StartStream(self.DeviceHandle, 0)  # start measuring
                self.ready = False
                self.armed = True
                #print('Armed OK')
                return True
            print('Not exists!')
        else:
            print('Sensor is not connected!')
        return False

    def disarm(self) -> list[(float, float)]:
        if self.connected and self.armed:
            exists = self.OphirCOM.IsSensorExists(self.DeviceHandle, 0)
            if exists:
                self.ready = False
                self.armed = False
                data = self.OphirCOM.GetData(self.DeviceHandle, 0)
                self.OphirCOM.StopStream(self.DeviceHandle, 0)

                events: list[(float, float)] = []
                for i in range(0, len(data[0]), 2):
                    events.append((data[1][i] - data[1][0], data[0][i]))
                self.ready = True
                #print('Disarmed OK')
                return events
            print('Not exists!')
        else:
            print('Sensor is not connected!')
        return []

    def __del__(self):
        if self.OphirCOM is not None:
            self.OphirCOM.StopAllStreams()
            self.OphirCOM.CloseAll()
            self.OphirCOM = None