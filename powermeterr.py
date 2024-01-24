import win32com.client
import csv

class OphirDevice:
    def __init__(self):
        self.OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
        self.DeviceList = []

    def scan_usb_devices(self):
        self.DeviceList = self.OphirCOM.ScanUSB()
        print("Connected Devices:", self.DeviceList)

    def open_device(self, index=0):
        DeviceHandle = self.OphirCOM.OpenUSBDevice(self.DeviceList[index])
        return DeviceHandle

    def configure_device(self, DeviceHandle, mode, wavelength, range_value):
        self.OphirCOM.ConfigureStreamMode(DeviceHandle, 0, 0, 0)
        self.OphirCOM.ConfigureStreamMode(DeviceHandle, 0, 2, 1)

        set_mode = self.OphirCOM.setMeasurementMode(DeviceHandle, 0, mode)  # 0 for power, 1 for energy, 2 for exposure
        set_range = self.OphirCOM.SetRange(DeviceHandle, 0, range_value)
        set_wavelength = self.OphirCOM.setWavelength(DeviceHandle, 0, wavelength)

        return set_mode, set_range, set_wavelength

    def start_stream(self, DeviceHandle):
        self.OphirCOM.StartStream(DeviceHandle, 0)

    def get_data(self, DeviceHandle):
        data = self.OphirCOM.GetData(DeviceHandle, 0)
        return data

    # def save_to_csv(self, events, csv_filename='power_data.csv'):
    #     with open(csv_filename, 'w', newline='') as csvfile:
    #         csv_writer = csv.writer(csvfile)
    #         csv_writer.writerow(['Time', 'Power'])  # Write header
    #         csv_writer.writerows(events)

def main():
    ophir_device = OphirDevice()
    ophir_device.scan_usb_devices()

    if not ophir_device.DeviceList:
        print("No Ophir device found. Exiting.")
        return

    selected_device_index = 0
    device_handle = ophir_device.open_device(selected_device_index)

    mode = 1  # 0 for power, 1 for energy, 2 for exposure
    
    # Show available ranges
    ranges = ophir_device.OphirCOM.GetRanges(device_handle, 0)
    print("Available Ranges:", ranges)

    range_value = int(input("Enter range: "))

    # Show available wavelengths
    wavelengths = ophir_device.OphirCOM.GetWavelengths(device_handle, 0)
    print("Available Wavelengths:", wavelengths)

    wavelength = int(input("Enter wavelength: "))

    ophir_device.configure_device(device_handle, mode, wavelength, range_value)
    ophir_device.start_stream(device_handle)

    data = ophir_device.get_data(device_handle)

    events = [(data[1][i] - data[1][0], data[0][i]) for i in range(0, len(data[0]), 2)]

    # ophir_device.save_to_csv(events)

if __name__ == "__main__":
    main()
