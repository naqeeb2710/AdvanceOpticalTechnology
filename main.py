from qcodes_contrib_drivers.drivers.Thorlabs.APT import Thorlabs_APT
import numpy as np
import matplotlib.pyplot as plt
from seabreeze.spectrometers import list_devices, Spectrometer
import time
import csv
import os

apt = Thorlabs_APT()

from qcodes_contrib_drivers.drivers.Thorlabs.K10CR1 import Thorlabs_K10CR1

inst = Thorlabs_K10CR1("K10CR1", 0, apt)

devices = list_devices()
if devices:
    print("Available devices:", devices)
else:
    print("No devices available.")


# # Move to zero and recalibrate
# inst.move_home()

# # Read position
# print("Position:", inst.position())

spec = Spectrometer(devices[0])

def perform_accumulation(spec, num_accumulations, exposure_time_micros, output_csv_filename):
    # Set integration time
    spec.integration_time_micros(exposure_time_micros)

    # Initialize lists to store wavelengths and intensities
    wavelengths = []
    intensities = [[] for _ in range(num_accumulations)]  # Initialize intensity_sum with zeros

    # Perform accumulation
    for i in range(num_accumulations):
        # Get wavelengths and intensities from data (assuming they are in nanometers)
        current_wavelengths = spec.wavelengths()
        current_intensities = spec.intensities()

        # Append the current wavelengths and intensities to the lists
        wavelengths.extend(current_wavelengths)
        intensities[i] = current_intensities
        
    # Create the "data" folder if it doesn't exist
    data_folder = 'data'
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    # Save the data to a CSV file in the "data" folder
    output_csv_filepath = os.path.join(data_folder, output_csv_filename)
    
    # Save the data to a CSV file
    with open(output_csv_filepath, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        header = ['Wavelength (nm'] + [f'Intensity AC {i + 1}' for i in range(num_accumulations)]
        csv_writer.writerow(header)  # Write header

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

    plt.savefig(output_plot_filepath, bbox_inches='tight', pad_inches=0)
    time.sleep(1.0)



# Define the initial angle, step size, and final angle
# Input for initial angle, step size, and final angle
initial_angle = float(input("Enter the initial angle in degrees: "))
step_size = float(input("Enter the step size in degrees: "))
final_angle = float(input("Enter the final angle in degrees: "))

# Define the number of accumulations and integration time
num_accumulations = int(input("Enter number of accumulation: "))
exposure_time_micros = float(input("Enter integration time in microseconds: "))

# Set the time delay (in seconds)
delay_seconds = 5

# Set target velocity to 10 deg/s
inst.velocity_max(10)

# Initialize the current angle to the initial angle
current_angle = initial_angle

# Loop to move the position
while current_angle <= final_angle:
    # Move to the current angle and wait until it's finished
    inst.position(current_angle)
    
    # Read and print the current position
    current_position = inst.position()
    time.sleep(0.5)  # Pause the execution for 0.5 seconds
    print(f"Position: {current_position} degrees at angle: {current_angle} degrees")
    
    time.sleep(delay_seconds)  # Pause the execution for delay_seconds
    
    # Dynamically generate the CSV filename based on the current angle
    current_csv_filename = f'angle_{current_angle}_integrationtime_{exposure_time_micros}_acc_{num_accumulations}.csv'
    
    # Take reading on spectrometer 
    perform_accumulation(spec, num_accumulations, exposure_time_micros,current_csv_filename)    
    
    # Increment the current angle by the step size
    current_angle += step_size
    
# Ensure that the final angle is reached
inst.position(final_angle)

# Read and print the final position
final_position = inst.position()
print(f"Final Position: {final_position} degrees")

# Close the instrument
inst.close()
apt.apt_clean_up()






