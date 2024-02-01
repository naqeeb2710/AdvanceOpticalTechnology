import win32com.client
import csv
import time
from datetime import datetime


def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
# Stop & Close all devices
OphirCOM.StopAllStreams() 
OphirCOM.CloseAll()


# Scan for connected Devices
DeviceList = OphirCOM.ScanUSB()
print(DeviceList)
Device = DeviceList[0]
DeviceHandle = OphirCOM.OpenUSBDevice(Device)
sensor = OphirCOM.GetSensorInfo(DeviceHandle, 0)
print(sensor)


# OphirCOM.ConfigureStreamMode(DeviceHandle, 0,0,0)
dataMode = OphirCOM.ConfigureStreamMode(DeviceHandle, 0,2,1)
# OphirCOM.DataReady(DeviceHandle, 0)
ready = True
OphirCOM.StartStream(DeviceHandle, 0)
time.sleep(0.05)
ready = False
# print(dataMode)



Data = OphirCOM.GetData(DeviceHandle,0)
print(Data)


csv_file_path = 'output_data.csv'

average_data_0 = sum(Data[0]) / len(Data[0])  # Assuming Data is a list of lists or a 2D array
average_data_0_nanojoules = average_data_0 * 1e9  # Convert average power to nanojoules
print(f'Average of Data[0] column: {average_data_0_nanojoules:.2f} nanojoules')


# Modify Data[1]
modified_data_1 = [data - Data[1][0] for data in Data[1]]

# Zip the arrays together with modified Data[1] to create rows for the CSV file
rows = zip(Data[0], modified_data_1, Data[2])

# Open the CSV file in write mode
with open(csv_file_path, 'w', newline='') as csv_file:
    # Create a CSV writer object
    csv_writer = csv.writer(csv_file)

    # Write the header (optional)
    csv_writer.writerow(['Energy', 'TimeStamp', 'Status'])  # Replace with actual column names

    # Write the data rows
    csv_writer.writerows(rows)

print(f'Data has been written to {csv_file_path}')

OphirCOM.StopStream(DeviceHandle, 0)
OphirCOM.Close(DeviceHandle)

if OphirCOM is not None:
    OphirCOM.StopAllStreams()
    OphirCOM.CloseAll()
    OphirCOM = None
