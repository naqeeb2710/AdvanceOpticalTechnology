import os
import time
import matplotlib.pyplot as plt
from seabreeze.spectrometers import list_devices, Spectrometer
import csv
import numpy as np
import tkinter as tk
from tkinter import filedialog
import shutil

class LiveSpectrum:
    def __init__(self):
        self.spec = None
        devices = list_devices()
        if devices:
            self.spec = Spectrometer(devices[0])
            print(devices[0],"for live spectrum")
        else:
            print("No spectrometer devices available.")
        self.fig = None
        self.plot_timestamps = []  # Initialize a list to store plot timestamps

    def live_spectrum(self, exposure_time_micros, max_plots=5):
        # Create a "plotdump" folder if it doesn't exist
        shutil.rmtree("plotdump", ignore_errors=True)
        os.makedirs("plotdump", exist_ok=True)

        # Function to update the plot with new data
        def update_plot(wavelengths, intensities):
            # Create the initial plot
            plt.figure(figsize=(12, 8))
            plt.plot(wavelengths, intensities)
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('Intensity')
            
            # Save the current plot as an image in the "plotdump" folder with a timestamp
            timestamp = time.strftime("%Y%m%d%H%M%S")
            plot_filename = f"plotdump/live_spectrum_{timestamp}.png"
            plt.savefig(plot_filename, bbox_inches='tight', pad_inches=0.5)
            plt.close()  # Close the plot to clear memory

            # Append the timestamp to the list of plot timestamps
            self.plot_timestamps.append(timestamp)

            # Remove the oldest plot file if the maximum number of plots is reached
            if len(self.plot_timestamps) > max_plots:
                # Get the filename of the previous plot
                prev_plot_timestamp = self.plot_timestamps.pop(0)
                prev_plot_filename = f"plotdump/live_spectrum_{prev_plot_timestamp}.png"
                # Check if the previous plot file exists, then remove it
                if os.path.exists(prev_plot_filename):
                    os.remove(prev_plot_filename)

            return plot_filename  # Return the path of the saved plot file

        # Main loop to continuously update the plot with live spectrum data
        try:
            while True:
                self.spec.integration_time_micros(exposure_time_micros)
                wavelengths, intensities = self.spec.spectrum()  # Replace with your spectrometer data acquisition
                latest_plot_path = update_plot(wavelengths, intensities)
                yield latest_plot_path  # Yield the latest plot path
        except KeyboardInterrupt:  # Handle KeyboardInterrupt to gracefully exit the loop
            self.spec.close()  # Close the spectrometer
    
    # def save_live_spectrum(self):
    #     # Stop the live spectrum loop
    #     wavelength, Intensity = self.spec.spectrum()
    #     plt.plot(wavelength, Intensity)
    #     plt.xlabel('Wavelength (nm)')
    #     plt.ylabel('Intensity')
    #     plt.savefig('BG_spectrum.png', bbox_inches='tight', pad_inches=0.5)
    #     if self.spec is not None:
    #         self.spec.close()  # Close the spectrometer
        
    #     # Get the current timestamp
    #     timestamp = time.strftime("%Y%m%d%H%M%S")
        
    #     # Save the wavelengths and intensities data to a CSV file
    #     data_filename = f"BG_spectrum_{timestamp}.csv"
    #     with open(data_filename, mode='w', newline='') as file:
    #         writer = csv.writer(file)
    #         writer.writerow(['Wavelength (nm)', 'Intensity'])
    #         # Replace the following line with the actual data from your spectrometer
    #         writer.writerows(zip(wavelength,Intensity)) # Example random dat
            
    #     print(f"Live spectrum data saved to {data_filename}")
    
    def save_live_spectrum(self, exposure_time_micros, experiment_name):
        # Stop the live spectrum loop
        # Get the current timestamp
        plt.close()
        self.spec.integration_time_micros(exposure_time_micros)
        wavelength, Intensity = self.spec.spectrum()
       
        if self.spec is not None:
            self.spec.close()  # Close the spectrometer

        # Create a Tkinter root window
        root = tk.Tk()
        root.withdraw()  # Hide the root window

        # Ask the user to select a directory for saving the files
        save_dir = filedialog.askdirectory(title="Select Directory")

        if save_dir:
            # Save the plot as an image
            plt.plot(wavelength, Intensity)
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('Intensity')
            plot_filename = os.path.join(save_dir, f'{experiment_name}_bg_{exposure_time_micros/1000.0}.png')
            plt.savefig(plot_filename, bbox_inches='tight', pad_inches=0.5)
            plt.close()

            # Save the data to a CSV file
            data_filename = os.path.join(save_dir, f'{experiment_name}_bg_{exposure_time_micros/1000.0}.csv')
            with open(data_filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Wavelength (nm)', 'Intensity'])
                writer.writerows(zip(wavelength, Intensity))

            print(f"Live spectrum data saved to {data_filename}")
        else:
            print("No directory selected.")

        # Close the Tkinter root window
        root.destroy()

    def close(self):
        if self.spec is not None:
            self.spec.close()
            self.spec = None
            print("Spectrometer closed successfully.")
