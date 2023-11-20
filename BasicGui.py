import tkinter as tk
from tkinter import ttk
from threading import Thread
import queue
import sys
from main_v2 import SpectrometerController  # Importing SpectrometerController from the other module
from main_v2 import MotorController  # Importing MotorController from the other module
from main_v2 import MeasurementController  # Importing MeasurementController from the other module

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Spectrometer Measurement App")

        # Initialize controllers
        self.spectrometer_controller = SpectrometerController()
        self.motor_controller = MotorController()
        # Move to zero and recalibrate
        self.motor_controller.move_home()

        # Set up GUI components
        self.create_widgets()

    def create_widgets(self):
        # Labels and Entry widgets for user input
        ttk.Label(self.root, text="Initial Angle (degrees):").grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
        self.initial_angle_entry = ttk.Entry(self.root)
        self.initial_angle_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self.root, text="Step Size (degrees):").grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
        self.step_size_entry = ttk.Entry(self.root)
        self.step_size_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(self.root, text="Final Angle (degrees):").grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
        self.final_angle_entry = ttk.Entry(self.root)
        self.final_angle_entry.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(self.root, text="Num Accumulations:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.E)
        self.num_accumulations_entry = ttk.Entry(self.root)
        self.num_accumulations_entry.grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(self.root, text="Exposure Time (microseconds):").grid(row=4, column=0, padx=10, pady=5, sticky=tk.E)
        self.exposure_time_entry = ttk.Entry(self.root)
        self.exposure_time_entry.grid(row=4, column=1, padx=10, pady=5)

        ttk.Label(self.root, text="Delay Time (seconds):").grid(row=5, column=0, padx=10, pady=5, sticky=tk.E)
        self.delay_time_entry = ttk.Entry(self.root)
        self.delay_time_entry.grid(row=5, column=1, padx=10, pady=5)

        ttk.Label(self.root, text="Target Velocity (deg/s):").grid(row=6, column=0, padx=10, pady=5, sticky=tk.E)
        self.target_velocity_entry = ttk.Entry(self.root)
        self.target_velocity_entry.grid(row=6, column=1, padx=10, pady=5)

        # Button to start measurement
        ttk.Button(self.root, text="Start Measurement", command=self.start_measurement).grid(row=7, column=0, columnspan=2, pady=10)
        # Quit button
        ttk.Button(self.root, text="Quit", command=self.quit_application).grid(row=8, column=0, columnspan=2, pady=10)
        # Bind the close button to the quit_application method
        self.root.protocol("WM_DELETE_WINDOW", self.quit_application)

    def start_measurement(self):
        try:
            # Get user input values
            initial_angle = float(self.initial_angle_entry.get())
            step_size = float(self.step_size_entry.get())
            final_angle = float(self.final_angle_entry.get())
            num_accumulations = int(self.num_accumulations_entry.get())
            exposure_time_micros = float(self.exposure_time_entry.get())
            delay_seconds = float(self.delay_time_entry.get())
            target_velocity = float(self.target_velocity_entry.get())

            # Connect to spectrometer
            self.spectrometer_controller.connect_spectrometer()

            # Configure motor
            self.motor_controller.configure_motor(target_velocity=target_velocity)

            # Create measurement controller
            measurement_controller = MeasurementController(self.spectrometer_controller, self.motor_controller)

            # Measure at angles with default velocity
            measurement_controller.measure_at_angles(
                initial_angle, final_angle, step_size, num_accumulations, exposure_time_micros, delay_seconds
            )

            # self.motor_controller.close_motor()
            # self.spectrometer_controller.disconnect_spectrometer()

        except Exception as e:
            print(f"An error occurred: {e}")

        # finally:
        #     # Disconnect spectrometer and close motor
        #     self.spectrometer_controller.disconnect_spectrometer()
        #     self.motor_controller.close_motor()
        #     root.quit()

    def quit_application(self):
        # Disconnect spectrometer and close motor when quitting the application
        self.spectrometer_controller.disconnect_spectrometer()
        self.motor_controller.close_motor()
        # self.root.destroy()
        sys.exit()

# Create the main application window
root = tk.Tk()
app = App(root)
# root.protocol("WM_DELETE_WINDOW", app.quit_application)  # Handle window close button
root.mainloop()
