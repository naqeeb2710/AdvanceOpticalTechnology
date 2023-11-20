import tkinter as tk
from tkinter import ttk
from threading import Thread
import queue
import sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import os
from main_v2 import SpectrometerController
from main_v2 import MotorController
from main_v2 import MeasurementController

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
        # Create frame for the first set of parameters
        frame1 = ttk.Frame(self.root, padding="10")
        frame1.grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(frame1, text="Initial Angle (degrees):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.initial_angle_entry = ttk.Entry(frame1)
        self.initial_angle_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame1, text="Final Angle (degrees):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.final_angle_entry = ttk.Entry(frame1)
        self.final_angle_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame1, text="Step Size (degrees):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        self.step_size_entry = ttk.Entry(frame1)
        self.step_size_entry.grid(row=2, column=1, padx=5, pady=5)

        # Create frame for the second set of parameters
        frame2 = ttk.Frame(self.root, padding="10")
        frame2.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(frame2, text="Target Velocity (deg/s):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.target_velocity_entry = ttk.Entry(frame2)
        self.target_velocity_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame2, text="Exposure Time (microseconds):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.exposure_time_entry = ttk.Entry(frame2)
        self.exposure_time_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame2, text="Num Accumulations:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        self.num_accumulations_entry = ttk.Entry(frame2)
        self.num_accumulations_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame2, text="Delay Time (seconds):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        self.delay_time_entry = ttk.Entry(frame2)
        self.delay_time_entry.grid(row=3, column=1, padx=5, pady=5)

        # Create a figure and axes to display the plot
        self.fig = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=1, column=0, columnspan=2, pady=10)

        # Button to start measurement
        ttk.Button(self.root, text="Start Measurement", command=self.start_measurement_thread).grid(row=2, column=0, pady=10)
        # Quit button
        ttk.Button(self.root, text="Quit", command=self.quit_application).grid(row=2, column=1, pady=10)
        # Bind the close button to the quit_application method
        self.root.protocol("WM_DELETE_WINDOW", self.quit_application)

    def start_measurement_thread(self):
        # Start a new thread for the measurement to avoid blocking the main thread
        thread = Thread(target=self.start_measurement)
        thread.start()

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
            
            # Access the current_csv_filename from the MeasurementController
            current_csv_filename = measurement_controller.current_csv_filename
            # Dynamically generate the plot filename based on the current angle
            output_plot_filename = current_csv_filename.replace('.csv', '.png')
            # Save the plot as an image file in the "plot" folder
            output_plot_filepath = os.path.join("plot", output_plot_filename)

            # Display the latest graph in the Tkinter application
            img = plt.imread(output_plot_filepath)
            self.ax.imshow(img)
            self.ax.axis('off')  # Turn off axis labels

            # Update the canvas
            self.canvas.draw()

        except Exception as e:
            print(f"An error occurred: {e}")

    def quit_application(self):
        # Disconnect spectrometer and close motor when quitting the application
        self.spectrometer_controller.disconnect_spectrometer()
        self.motor_controller.close_motor()
        self.root.quit()
        self.root.destroy()
        sys.exit()

# Create the main application window
root = tk.Tk()
app = App(root)
root.mainloop()
