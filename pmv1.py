import win32com.client
import csv
from datetime import datetime
import time

class OphirMeasurement:
    def __init__(self):
        self.OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
        self.DeviceHandle = None
        self.csv_file_path = 'output_data.csv'

    def timestamp_to_datetime(self, timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def connect_device(self):
        # Stop & Close all devices
        self.OphirCOM.StopAllStreams() 
        self.OphirCOM.CloseAll()
        
        # Scan for connected Devices
        DeviceList = self.OphirCOM.ScanUSB()
        print(DeviceList)
        self.Device = DeviceList[0]
        self.DeviceHandle = self.OphirCOM.OpenUSBDevice(self.Device)
        sensor = self.OphirCOM.GetSensorInfo(self.DeviceHandle, 0)
        print(sensor)

    def start_stream(self):
        # Configure stream mode
        dataMode = self.OphirCOM.ConfigureStreamMode(self.DeviceHandle, 0, 2, 1)
        self.OphirCOM.StartStream(self.DeviceHandle, 0)
        time.sleep(0.05)

    def stop_stream(self):
        self.OphirCOM.StopStream(self.DeviceHandle, 0)
        self.OphirCOM.Close(self.DeviceHandle)

    def write_to_csv(self, Data):
        average_data_0 = sum(Data[0]) / len(Data[0])  
        average_data_0_nanojoules = average_data_0 * 1e9  
        print(f'Average of Data[0] column: {average_data_0_nanojoules:.2f} nanojoules')

        modified_data_1 = [data - Data[1][0] for data in Data[1]]
        rows = zip(Data[0], modified_data_1, Data[2])

        with open(self.csv_file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Energy', 'TimeStamp', 'Status']) 
            csv_writer.writerows(rows)
        print(f'Data has been written to {self.csv_file_path}')

    def cleanup(self):
        if self.OphirCOM is not None:
            self.OphirCOM.StopAllStreams()
            self.OphirCOM.CloseAll()
            self.OphirCOM = None

def main(iterations, file_number):
    # Initialize OphirMeasurement object
    ophir = OphirMeasurement()
    
    try:
        # Connect to the device
        ophir.connect_device()
        
        # Start stream and perform actions
        for i in range(iterations):
            ophir.start_stream()
            # Do something with the stream data
            
            # Simulating processing time
            time.sleep(2)
            
            # Stop stream and write data to CSV with file_number
            ophir.stop_stream()
            ophir.write_to_csv(f'output_data_{file_number}_{i}.csv')
        
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Clean up resources
        ophir.cleanup()

if __name__ == "__main__":
    iterations = int(input("Enter the number of iterations: "))
    file_number = int(input("Enter the output file number: "))
    main(iterations, file_number)

