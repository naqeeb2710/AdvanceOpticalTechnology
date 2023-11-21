import os
import time
import matplotlib.pyplot as plt
import csv
from seabreeze.spectrometers import list_devices, Spectrometer
from qcodes_contrib_drivers.drivers.Thorlabs.APT import Thorlabs_APT
from qcodes_contrib_drivers.drivers.Thorlabs.K10CR1 import Thorlabs_K10CR1


class SpectrometerController:
    def __init__(self):
        self.spec = None
        devices = list_devices()
        if devices:
            self.spec = Spectrometer(devices[0])
            print(devices[0])
        else:
            print("No spectrometer devices available.")

    # def connect_spectrometer(self):
    #     devices = list_devices()
    #     if devices:
    #         self.spec = Spectrometer(devices[0])
    #         # print(devices[0])
    #     else:
    #         print("No spectrometer devices available.")

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
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(wavelengths[:len(current_wavelengths)], intensities[0])

        # Label the x and y axes
        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Intensity')

        # Add angle and exposure time information inside the plot

        info_text = f"Angle: {MeasurementController.current_angle}°\nExp Time: {exposure_time_micros} µs"
        ax.text(0.95, 0.95, info_text, transform=ax.transAxes, verticalalignment='top', horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.savefig(output_plot_filepath, bbox_inches='tight', pad_inches=0)
        time.sleep(1.0)

    def disconnect_spectrometer(self):
        if self.spec is not None:
            self.spec.close()


class MotorController:
    def __init__(self):
        self.apt = Thorlabs_APT()
        self.inst = Thorlabs_K10CR1("K10CR1", 0, self.apt)
    
    def move_home(self):
        self.inst.move_home()

    def configure_motor(self, target_velocity):
        if hasattr(self.inst, 'velocity_max'):
            self.inst.velocity_max(0) # Set velocity to 0 before cleanup
        self.inst.velocity_max(target_velocity)

    def move_to_angle(self, angle):
        self.inst.position(angle)

    def close_motor(self):
        if hasattr(self.inst, 'velocity_max'):
            self.inst.velocity_max(0)  # Set velocity to 0 before cleanup
        self.inst.close()
        self.apt.apt_clean_up()

class MeasurementController:
    def __init__(self, spectrometer_controller, motor_controller):
        self.spectrometer_controller = spectrometer_controller
        self.motor_controller = motor_controller
        self.current_csv_filename = None

    def measure_at_angles(self, initial_angle, final_angle, step_size, num_accumulations, exposure_time_micros, delay_seconds):
        current_angle = initial_angle

        while current_angle <= final_angle:
            self.motor_controller.move_to_angle(current_angle)
            current_position = self.motor_controller.inst.position()
            time.sleep(0.5)  # Pause the execution for 0.5 seconds
            print(f"Position: {current_position} degrees at angle: {current_angle} degrees")
            time.sleep(delay_seconds)

            # Update the class variable
            MeasurementController.current_angle = current_angle

            self.current_csv_filename = f'angle_{current_angle}_integrationtime_{exposure_time_micros}_acc_{num_accumulations}.csv'
            self.spectrometer_controller.perform_accumulation(num_accumulations, exposure_time_micros, self.current_csv_filename)

            current_angle += step_size

        self.motor_controller.move_to_angle(final_angle)
        final_position = self.motor_controller.inst.position()
        print(f"Final Position: {final_position} degrees")


def main():
    spectrometer_controller = SpectrometerController()
    motor_controller = MotorController()

    # Move to zero and recalibrate
    motor_controller.move_home()

    try:
        # Connect to spectrometer
        # spectrometer_controller.connect_spectrometer()
        

        # Input parameters
        initial_angle = float(input("Enter the initial angle in degrees: "))
        step_size = float(input("Enter the step size in degrees: "))
        final_angle = float(input("Enter the final angle in degrees: "))
        num_accumulations = int(input("Enter number of accumulations: "))
        exposure_time_micros = float(input("Enter integration time in microseconds: "))
        delay_seconds = 5

        # Take target velocity from the user
        target_velocity = float(input("Enter the target velocity in deg/s: "))
        motor_controller.configure_motor(target_velocity=target_velocity)

        # Create measurement controller
        measurement_controller = MeasurementController(spectrometer_controller, motor_controller)

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
