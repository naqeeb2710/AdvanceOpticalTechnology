import tkinter as tk
from tkinter import ttk
from threading import Thread
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

        # Set up GUI components
        self.create_widgets()

    def create_widgets(self):
        # Create frame for the first set of parameters
        frame1 = ttk.Frame(self.root, padding="10", name="frame1", borderwidth=2, relief="groove")
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

        # Create a frame for the second set of parameters
        frame2 = ttk.Frame(self.root, padding="10", name="frame2", borderwidth=2, relief="groove")
        frame2.grid(row=0, column=3, padx=10, pady=10)

        ttk.Label(frame2, text="Target Velocity (deg/s):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.target_velocity_entry = ttk.Entry(frame2)
        self.target_velocity_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame2, text="Exposure Time (microseconds):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.exposure_time_entry = ttk.Entry(frame2)
        self.exposure_time_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame2, text="Num Accumulations:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        self.num_accumulations_entry = ttk.Entry(frame2)
        self.num_accumulations_entry.grid(row=2, column=1, padx=5, pady=5)

        # Create a frame for the third set of parameters (single test)
        frame3 = ttk.Frame(self.root, padding="10", name="frame3", borderwidth=2, relief="groove")
        frame3.grid(row=0, column=6, padx=10, pady=10)

        ttk.Label(frame3, text="Single Test Angle (degrees):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.single_test_angle_entry = ttk.Entry(frame3)
        self.single_test_angle_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame3, text="Single Test Accumulations:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.single_test_accumulations_entry = ttk.Entry(frame3)
        self.single_test_accumulations_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame3, text="Single Test Exposure Time (µs):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        self.single_test_exposure_time_entry = ttk.Entry(frame3)
        self.single_test_exposure_time_entry.grid(row=2, column=1, padx=5, pady=5)

        # Create a horizontal frame for buttons and progress bar (2:1 ratio)
        button_frame = ttk.Frame(self.root, padding="10", name="button_frame", borderwidth=2, relief="groove")
        button_frame.grid(row=1, column=0, columnspan=3, pady=10)

        # Home button
        ttk.Button(button_frame, text="Home", command=self.motor_controller.move_home).grid(row=0, column=0, padx=(5, 5), pady=5)

        # Start Measurement button
        ttk.Button(button_frame, text="Start Measurement", command=self.start_measurement_thread).grid(row=0, column=1, padx=(5, 5), pady=5)

        # Progress bar
        ttk.Label(button_frame, text="Progress:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        self.progress_label = ttk.Label(button_frame, text="0%")
        self.progress_label.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.progress_bar = ttk.Progressbar(button_frame, orient='horizontal', length=130, mode='determinate')
        self.progress_bar.grid(row=0, column=4, padx=(0, 5), pady=5)  # Adjusted the padx to shift the progress bar to the left

        # Quit button
        ttk.Button(button_frame, text="Quit", command=self.quit_application).grid(row=0, column=6, padx=(5, 5), pady=5)
        # Bind the close button to the quit_application method
        self.root.protocol("WM_DELETE_WINDOW", self.quit_application)

        # Button for performing a single test
        ttk.Button(button_frame, text="Single Test", command=self.perform_single_test).grid(row=0, column=5, pady=5)

        # Create a frame for angle adjustment
        angle_adjust_frame = ttk.Frame(self.root, padding="10", name="angle_adjust_frame", borderwidth=2, relief="groove")
        angle_adjust_frame.grid(row=1, column=3, pady=10)

        ttk.Label(angle_adjust_frame, text="Angle Size:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.angle_size_entry = ttk.Entry(angle_adjust_frame)
        self.angle_size_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(angle_adjust_frame, text="Up Angle", command=self.up_angle).grid(row=0, column=2, padx=(5, 5), pady=5)
        ttk.Button(angle_adjust_frame, text="Down Angle", command=self.down_angle).grid(row=0, column=3, padx=(5, 5), pady=5)

        # Create a figure and axes to display the plot
        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=4, column=0, columnspan=4, pady=10)
    
    def up_angle(self):
        # Implement the logic for increasing the angle
        current_angle = self.motor_controller.inst.position()
        self.motor_controller.move_to_angle(current_angle + float(self.angle_size_entry.get()))

    def down_angle(self):
        # Implement the logic for decreasing the angle
        current_angle = self.motor_controller.inst.position()
        self.motor_controller.move_to_angle(current_angle - float(self.angle_size_entry.get()))

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
            target_velocity = float(self.target_velocity_entry.get())

            # Configure motor
            self.motor_controller.configure_motor(target_velocity=target_velocity)

            # Create measurement controller
            measurement_controller = MeasurementController(self.spectrometer_controller, self.motor_controller)

            # Clear previous plot
            self.ax.clear()

            # Measure at angles with default velocity using a while loop
            total_steps = ((final_angle - initial_angle) / step_size) + 1
            current_step = 1

            while current_step <= total_steps:
                angle = (initial_angle + (current_step - 1) * step_size)
                
                measurement_controller.measure_at_angles(
                    angle, angle, 1, num_accumulations, exposure_time_micros, 3  # Fixed delay of 3 seconds
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

                # Update the progress bar
                progress_value = current_step / total_steps * 100
                self.progress_label.config(text=f"{progress_value:.1f}%")
                self.progress_bar['value'] = progress_value
                self.root.update()

                # Delay for a short time before the next measurement
                self.root.after(100)  # Adjust the delay time as needed

                # Increment the current_step for the next iteration
                current_step += 1

            # Clear input fields after the calculation
            self.initial_angle_entry.delete(0, tk.END)
            self.final_angle_entry.delete(0, tk.END)
            self.step_size_entry.delete(0, tk.END)
            self.target_velocity_entry.delete(0, tk.END)
            self.exposure_time_entry.delete(0, tk.END)
            self.num_accumulations_entry.delete(0, tk.END)

        except Exception as e:
            print(f"An error occurred: {e}")
            # Close motor and spectrometer in case of an error
            self.motor_controller.close_motor()
            self.spectrometer_controller.disconnect_spectrometer()
        
    def perform_single_test(self):
        try:
        # Get user input values for single test
            single_test_angle = float(self.single_test_angle_entry.get())
            single_test_accumulations = int(self.single_test_accumulations_entry.get())
            single_test_exposure_time_micros = float(self.single_test_exposure_time_entry.get())

            # Create measurement controller
            measurement_controller = MeasurementController(self.spectrometer_controller, self.motor_controller)

            # Clear previous plot
            self.ax.clear()

            # Perform a single test at the specified angle
            measurement_controller.measure_at_angles(
                single_test_angle, single_test_angle, 1, single_test_accumulations, single_test_exposure_time_micros, 3
            )  # Fixed delay of 3 seconds

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
            print(f"An error occurred during single test: {e}")
            self.spectrometer_controller.disconnect_spectrometer()
            self.motor_controller.close_motor()

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
