import os
import time
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import csv
from sensor import Sensor
from seabreeze.spectrometers import list_devices, Spectrometer
from qcodes_contrib_drivers.drivers.Thorlabs.APT import Thorlabs_APT
from qcodes_contrib_drivers.drivers.Thorlabs.K10CR1 import Thorlabs_K10CR1

def time_counter(start_time, end_time, operation_name):
    elapsed_time = end_time - start_time
    print(f"{operation_name} took {elapsed_time:.2f} seconds")


class SpectrometerController:
    def __init__(self):
        self.spec = None
        devices = list_devices()
        if devices:
            self.spec = Spectrometer(devices[0])
            print(devices[0])
        else:
            print("No spectrometer devices available.")
        

    def perform_accumulation(self, num_accumulations, exposure_time_micros, output_csv_filename):
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
        data_folder = 'data'
        os.makedirs(data_folder, exist_ok=True)

        # Save the data to a CSV file in the "data" folder
        output_csv_filepath = os.path.join(data_folder, output_csv_filename)
        with open(output_csv_filepath, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            header = ['Wavelength (nm'] + [f'Intensity AC {i + 1}' for i in range(num_accumulations)]
            csv_writer.writerow(header)

            for row in zip(wavelengths, *intensities):
                csv_writer.writerow(row)
        

        # Create the "plot" folder if it doesn't exist
        plot_folder = 'plot'
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
        info_text = f"Angle: {MeasurementController.current_angle}°\nExp Time: {exposure_time_micros/1000.0} ms"
        ax.text(0.98, 0.98, info_text, transform=ax.transAxes, verticalalignment='top', horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='wheat', alpha=1))

        plt.savefig(output_plot_filepath, bbox_inches='tight', pad_inches=0.5)
        time.sleep(1.0)
        
    def disconnect_spectrometer(self):
        if self.spec is not None:
            self.spec.close()


class MotorController:
    def __init__(self):
        self.apt = Thorlabs_APT()
        self.inst = Thorlabs_K10CR1("K10CR1", 0, self.apt)
        self.inst.velocity_max(25)
        self.inst._set_velocity_acceleration(25)
    
    def move_home(self):
        if hasattr(self.inst, 'velocity_max'):
            self.inst.velocity_max(25) # Set velocity to 0 before cleanup
        self.inst.velocity_max(25)
        self.inst.move_home()

    def configure_motor(self, target_velocity):
        if hasattr(self.inst, 'velocity_max'):
            self.inst.velocity_max(0) # Set velocity to 0 before cleanup
        self.inst.velocity_max(25)

    def move_to_angle(self, angle):
        self.inst.position(angle)

    def close_motor(self):
        if hasattr(self.inst, 'velocity_max'):
            self.inst.velocity_max(0)  # Set velocity to 0 before cleanup
        self.inst.close()
        self.apt.apt_clean_up()

class MeasurementController:
    def __init__(self, spectrometer_controller, motor_controller, experiment_name):
        self.spectrometer_controller = spectrometer_controller
        self.motor_controller = motor_controller
        self.current_csv_filename = None
        self.power_meter = Sensor()
        self.experiment_name = experiment_name  # Add an experiment name attribute
        self.default_measurement_range = 3  # Default measurement range is 20.0nJ
        self.threshold_status_count = 10  # Threshold for status count
        

    def measure_at_angles(self, initial_angle, final_angle, step_size, num_accumulations, exposure_time_micros, delay_seconds):
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
            current_position = self.motor_controller.inst.position()
            # time.sleep(0.5)  # Pause the execution for 0.5 seconds
            print(f"Position: {current_position} degrees at angle: {current_angle_normalized} degrees")
            time.sleep(delay_seconds)

            # Update the class variable
            MeasurementController.current_angle = current_angle_normalized

            self.current_csv_filename = f'{self.experiment_name}_angle_{int(current_angle_normalized)}_integrationtime_{int(exposure_time_micros)}_acc_{num_accumulations}.csv'
            self.spectrometer_controller.perform_accumulation(num_accumulations, exposure_time_micros, self.current_csv_filename)
            self.power_meter.connect()
            # time.sleep(0.5)
            self.power_meter.arm()
            power_data, average_power = self.power_meter.disarm()  # Unpack the tuple to get power data and average power
            if power_data:
                print("Power data recorded:")
                power_meter_filename = os.path.join(dump_folder, f'power_meter_dump_{self.experiment_name}_angle_{current_angle_normalized}.csv')
                with open(power_meter_filename, 'w') as power_dump:
                    # Write header
                    power_dump.write('time, power, status\n')
                    # Write data rows
                    for event in power_data:
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
                self.power_meter.arm()
                power_data, average_power = self.power_meter.disarm()  # Unpack the tuple to get power data and average power
            else:
                status_counter = 0  # Reset status counter if not exceeded threshold

            angle_power_list.append([current_angle, average_power])
            current_angle += step_size

        # Move to the final angle after completing the loop
        final_angle_normalized = final_angle % 360
        self.motor_controller.move_to_angle(final_angle_normalized)
        final_position = self.motor_controller.inst.position()
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
        # plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%.2f'))  # Set x-axis formatter
        # plt.gca().yaxis.set_major_formatter(FormatStrFormatter('%.2f'))  # Set y-axis formatter
        plt.yticks([i for i in range(0, int(max(powers)) + 5, 5)])  # Set ticks at intervals of 2
        # plt.ylim(0, max(powers) * 1.2)  # Increase y-axis scale by 20%
        plt.savefig(f'{self.experiment_name}_angle_power.png', bbox_inches='tight', pad_inches=0.5)
        measurement_range = self.default_measurement_range  # Reset measurement range to default
        self.power_meter.measurement_range = measurement_range
        self.power_meter.connect()
        self.power_meter.arm()
        self.power_meter.disarm()  

def main():
    spectrometer_controller = SpectrometerController()
    motor_controller = MotorController()

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

        # Take target velocity from the user
        target_velocity = float(input("Enter the target velocity in deg/s: "))
        motor_controller.configure_motor(target_velocity=target_velocity)

        # Create measurement controller
        measurement_controller = MeasurementController(spectrometer_controller, motor_controller,experiment_name)

        # Measure at angles with default velocity
        measurement_controller.measure_at_angles(
            initial_angle, final_angle, step_size, num_accumulations, exposure_time_micros, delay_seconds
        )

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close both spectrometer and motor controller
        spectrometer_controller.disconnect_spectrometer()
        motor_controller.close_motor()


if __name__ == "__main__":
    main()
