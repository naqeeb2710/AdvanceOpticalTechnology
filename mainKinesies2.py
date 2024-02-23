import os
import time
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import csv
from sensor import Sensor
from seabreeze.spectrometers import list_devices, Spectrometer
import csv
import numpy as np
from matplotlib.widgets import Button
from ctypes import *
import sys


class SpectrometerController:
    def __init__(self):
        self.spec = None
        devices = list_devices()
        if devices:
            self.spec = Spectrometer(devices[0])
            print(devices[0])
        else:
            print("No spectrometer devices available.")
        self.fig = None  # Initialize figure object to store the reference of the plot window
        

    def perform_accumulation(self, num_accumulations, exposure_time_micros, output_csv_filename,save_dir):
        if self.spec is None:
            print("Spectrometer not connected. Please connect first.")
            return

        # Set integration time
        self.spec.integration_time_micros(exposure_time_micros)

        # Initialize lists to store wavelengths and intensities
        wavelengths = []
        intensities = [[] for _ in range(num_accumulations)]

        # Perform accumulation
        for i in range(num_accumulations):
            current_wavelengths = self.spec.wavelengths()
            current_intensities = self.spec.intensities()

            wavelengths.extend(current_wavelengths)
            intensities[i] = current_intensities

        # Create the "data" folder if it doesn't exist
        data_folder = save_dir
        os.makedirs(data_folder, exist_ok=True)

        # Save the data to a CSV file in the "data" folder
        output_csv_filepath = os.path.join(data_folder, output_csv_filename)
        with open(output_csv_filepath, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            header = ['Wavelength (nm)'] + [f'Intensity AC {i + 1}' for i in range(num_accumulations)]
            csv_writer.writerow(header)

            for row in zip(wavelengths, *intensities):
                csv_writer.writerow(row)
        

        # Create the "plot" folder if it doesn't exist
        plot_folder = save_dir
        if not os.path.exists(plot_folder):
            os.makedirs(plot_folder)

        # Dynamically generate the plot filename based on the current angle
        output_plot_filename = output_csv_filename.replace('.csv', '.png')
        # Save the plot as an image file in the "plot" folder
        output_plot_filepath = os.path.join(plot_folder, output_plot_filename)
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111)
        ax.plot(wavelengths[:len(current_wavelengths)], intensities[0])

        # Label the x and y axes
        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Intensity')

        # Add angle and exposure time information inside the plot
        info_text = f"Angle:{MeasurementController.current_angle}° \n Exp Time: {exposure_time_micros/1000.0} ms"
        ax.text(0.98, 0.98, info_text, transform=ax.transAxes, verticalalignment='top', horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='wheat', alpha=1))

        plt.savefig(output_plot_filepath, bbox_inches='tight', pad_inches=0.5)
        time.sleep(1.0)
    
    def close_plot(self):
        if self.fig is not None:
            plt.close(self.fig)

    def disconnect_spectrometer(self):
        if self.spec is not None:
            self.spec.close()

class ThorlabsMotionController:
    def __init__(self):
        self.lib = None
        self.serial_num = c_char_p(b"55357574")
        self.STEPS_PER_REV = c_double(136533)  # for the K10CR1
        self.gbox_ratio = c_double(1.0)  # gearbox ratio
        self.pitch = c_double(1.0)
        self.dll_path = r"C:\Program Files\Thorlabs\Kinesis"
        print("Initializing Thorlabs Motion Controller")

        if sys.version_info < (3, 8):
            os.chdir(self.dll_path)
        else:
            os.add_dll_directory(self.dll_path)

        self.lib = cdll.LoadLibrary("Thorlabs.MotionControl.KCube.DCServo.dll")

    def open_device(self):
        if self.lib.TLI_BuildDeviceList() == 0:
            self.lib.CC_Open(self.serial_num)
            # print("ND filter Connected")
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

    def current_position(self):
        self.open_device()
        self.lib.CC_RequestPosition(self.serial_num)
        time.sleep(0.1)
        current_position = self.lib.CC_GetPosition(self.serial_num)
        self.close_device()
        return current_position/136533

    def delaytime(self,angle):
        self.open_device()
        self.lib.CC_RequestPosition(self.serial_num)
        time.sleep(0.1)
        current=(self.lib.CC_GetPosition(self.serial_num)/self.STEPS_PER_REV.value)
        # print("Current Position: ",current)
        # if angle == 0:
        #     delay=1
        #     print("Delay: ",delay)
        # else :
        delay= (abs(angle - current ))/25
        delay=delay+1
        print("Delay: ",delay)
        self.close_device()
        return delay
    
    def move_to_angle(self, angle):
        self.open_device()
        steps = int(angle * self.STEPS_PER_REV.value)
        self.lib.CC_MoveToPosition(self.serial_num, steps)
        CC_SetVelParams = self.lib.CC_SetVelParams
        CC_SetVelParams.argtypes = [c_char_p, c_int, c_int]
        CC_SetVelParams.restype = c_short
        acceleration_value = 1502*25
        max_velocity_value = 25*7329109
        self.lib.CC_SetVelParams(self.serial_num, acceleration_value, max_velocity_value)
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


class MeasurementController:
    def __init__(self, spectrometer_controller, motor_controller, experiment_name):
        self.spectrometer_controller = spectrometer_controller
        self.motor_controller = motor_controller
        self.current_csv_filename = None
        self.power_meter = Sensor()
        self.experiment_name = experiment_name  # Add an experiment name attribute
        self.default_measurement_range = 3  # Default measurement range is 20.0nJ
        self.threshold_status_count = 5  # Threshold for status count

    def measure_power_at_angles(self, initial_angle, final_angle,step_size, delay_seconds):
        current_angle = initial_angle
        angle_power_list = []  # Initialize an empty list to store angle-power pairs
        dump_folder = 'dump'
        os.makedirs(dump_folder, exist_ok=True)
        measurement_range = self.default_measurement_range  # Initialize measurement range 
        self.power_meter.measurement_range = measurement_range
        print(self.power_meter.measurement_range)
        status_counter = 0  # Initialize status counter
        self.power_meter.connect()

        while current_angle <= final_angle:
            # Convert the angle to be within the range [0, 360)
            current_angle_normalized = current_angle % 360

            self.motor_controller.move_to_angle(current_angle_normalized)
            current_position = self.motor_controller.current_position()
            # time.sleep(0.5)  # Pause the execution for 0.5 seconds
            print(f"Position: {current_position} degrees at angle")
            time.sleep(delay_seconds)

            # Update the class variable
            # MeasurementController.current_angle = current_angle_normalized

            self.power_meter.connect()
            # time.sleep(0.1)
            self.power_meter.arm()
            power_data, average_power = self.power_meter.disarm() # Unpack the tuple to get power data and average power
            if power_data:
                print(power_data)
                print("Power data recorded:")
                power_meter_filename = os.path.join(dump_folder, f'power_meter_dump_{self.experiment_name}_angle_{current_angle_normalized}.csv')
                with open(power_meter_filename, 'w') as power_dump:
                    # Write header
                    power_dump.write('time, power, status\n')
                    # Write data rows
                    for event in power_data:
                        print(power_data)
                        if event[2]==0:
                            power_dump.write('%.3f, %.2e, %.2f\n' % (event[0], event[1], event[2]))
                        if self.power_meter.measurement_range == 3:  # Check if not already in 200nJ range
                            if event[2] == 1:  # Check if data indicates status change
                                status_counter += 1
                                print('status counter = ', status_counter)
            else:
                print("No power data recorded.")
            # Check if status counter exceeds threshold
            if status_counter > self.threshold_status_count:
                measurement_range = 2  # Change to 200nJ range
                self.power_meter.measurement_range = measurement_range
                status_counter = 0  # Reset status counter after changing the range
                self.power_meter.connect()
                # time.sleep(0.1)
                self.power_meter.arm()
                power_data, average_power = self.power_meter.disarm()
                if power_data:
                    print(power_data)
                    print("Power data recorded:")
                    power_meter_filename = os.path.join(dump_folder, f'power_meter_dump_{self.experiment_name}_angle_{current_angle_normalized}.csv')
                    with open(power_meter_filename, 'w') as power_dump:
                        # Write header
                        power_dump.write('time, power, status\n')
                        # Write data rows
                        for event in power_data:
                            power_dump.write('%.3f, %.2e, %.2f\n' % (event[0], event[1], event[2]))
                  # Unpack the tuple to get power data and average power
            else:
                status_counter = 0  # Reset status counter if not exceeded threshold

            angle_power_list.append([current_angle, average_power])
            current_angle += step_size

        # Move to the final angle after completing the loop
        final_angle_normalized = final_angle % 360
        self.motor_controller.move_to_angle(final_angle_normalized)
        final_position = self.motor_controller.current_position()
        print(f"Final Position: {final_position} degrees")
        print(angle_power_list)
        # Save the angle-power list to a CSV file

        with open(f'{self.experiment_name}_angle_power.csv', 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            header = ['Angle (deg)', 'Average Power (nJ)']
            csv_writer.writerow(header)
            for row in angle_power_list:
                csv_writer.writerow(row)

        angles, powers = zip(*angle_power_list)
        plt.figure(figsize=(12, 8))
        plt.scatter(angles, powers)
        plt.xlabel('Angle (deg)')
        plt.ylabel('Average Power (nJ)')
        plt.yticks([i for i in range(0, int(max(powers)) + 5, 5)])  # Set ticks at intervals of 2
        plt.savefig(f'{self.experiment_name}_angle_power.png', bbox_inches='tight', pad_inches=0.5)

    def measure_at_angles(self, initial_angle, final_angle, step_size, num_accumulations, exposure_time_micros, delay_seconds,save_dir):
        current_angle = initial_angle

        while current_angle <= final_angle:
            # Convert the angle to be within the range [0, 360)
            current_angle_normalized = current_angle % 360

            delay=self.motor_controller.delaytime(current_angle_normalized)
            self.motor_controller.move_to_angle(current_angle_normalized)
            time.sleep(delay)

            current_position = self.motor_controller.current_position()
            # time.sleep(0.5)  # Pause the execution for 0.5 seconds
            print(f"Position: {current_position} degrees at angle")
            # time.sleep(delay_seconds)

            # Update the class variable
            MeasurementController.current_angle = current_position

            self.current_csv_filename = f'{self.experiment_name}_spec_{int(current_position)}deg_{int(exposure_time_micros/1000.0)}ms_acc_{num_accumulations}.csv'
            self.spectrometer_controller.perform_accumulation(num_accumulations, exposure_time_micros, self.current_csv_filename,save_dir)
            current_angle += step_size

        # Move to the final angle after completing the loop
        final_angle_normalized = final_angle % 360
        self.motor_controller.move_to_angle(final_angle_normalized)
        final_position = self.motor_controller.current_position()
        print(f"Final Position: {final_position} degrees")

def main():
    spectrometer_controller = SpectrometerController()
    motor_controller = ThorlabsMotionController()

    # Move to zero and recalibrate
    # do you want to go home 
    if input("Do you want to go home? (y/n): ") == 'y':
        motor_controller.move_home()

    try:
        # Input parameters
        experiment_name = input("Enter the experiment name: ")  # Add an experiment name input
        initial_angle = float(input("Enter the initial angle in degrees: "))
        step_size = float(input("Enter the step size in degrees: "))
        final_angle = float(input("Enter the final angle in degrees: "))
        num_accumulations = int(input("Enter number of accumulations: "))
        exposure_time_ms = float(input("Enter integration time in milliseconds: "))
        # Convert milliseconds to microseconds
        exposure_time_micros = exposure_time_ms * 1000.0
        delay_seconds = 0.5

        # Create measurement controller
        measurement_controller = MeasurementController(spectrometer_controller, motor_controller,experiment_name)

        # Ask the user for the action to perform
        action = input("What action do you want to perform? (P: Power, S: Spectrum): ")

        if action == 'p':
            # Perform accumulation
            measurement_controller.measure_power_at_angles(initial_angle, final_angle, step_size,delay_seconds)
        elif action == 's':
            # Measure power at angles
            measurement_controller.measure_at_angles(
                initial_angle, final_angle, step_size, num_accumulations, exposure_time_micros, delay_seconds
            )
        else:
            print("Invalid action selected. Please choose 'a' for accumulation or 'p' for power measurement.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close both spectrometer and motor controller
        spectrometer_controller.disconnect_spectrometer()
      


if __name__ == "__main__":
    main()
