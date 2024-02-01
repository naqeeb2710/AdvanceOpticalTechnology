import tkinter as tk
from tkinter import ttk, IntVar
from threading import Thread
import sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import os
from main_v3 import SpectrometerController
from main_v3 import MotorController
from main_v3 import MeasurementController
# import sensor

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Amplified Spontaneous Emission Measurement App")

        # Initialize controllers
        self.spectrometer_controller = SpectrometerController()
        self.motor_controller = MotorController()
        # self.sensor = Sensor()

        # Create IntVar to store checkbox state
        self.go_home_var = IntVar(value=1)  # Default to checked

        # Set up GUI components
        self.create_widgets()
        self.update_current_info()

    def create_widgets(self):
        # Create a container frame for the layout
        container_frame = ttk.Frame(self.root, padding="10")
        container_frame.grid(row=0, column=0, rowspan=2, columnspan=4, padx=10, pady=10)

        # Create frame for the first set of parameters
        frame1 = ttk.Frame(container_frame, padding="10", name="frame1", borderwidth=2, relief="groove")
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

        #create a input for experiment name
        ttk.Label(frame1, text="Sample name:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        self.experiment_name_entry = ttk.Entry(frame1)
        self.experiment_name_entry.grid(row=3, column=1, padx=5, pady=5)

        # Create a frame for the second set of parameters
        frame2 = ttk.Frame(container_frame, padding="10", name="frame2", borderwidth=2, relief="groove")
        frame2.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(frame2, text="Target Velocity (deg/s):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.target_velocity_entry = ttk.Entry(frame2)
        self.target_velocity_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame2, text="Exposure Time (ms):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.exposure_time_entry = ttk.Entry(frame2)
        self.exposure_time_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame2, text="Num Accumulations:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        self.num_accumulations_entry = ttk.Entry(frame2)
        self.num_accumulations_entry.grid(row=2, column=1, padx=5, pady=5)

        # Create a checkbox for "Go Home" or "After Measurement" in frame2
        self.go_home_checkbox = ttk.Checkbutton(frame2, text="Go Home After Measurement", variable=self.go_home_var)
        self.go_home_checkbox.grid(row=3, column=0, columnspan=2, pady=5, sticky=tk.W) 

        # Create a frame for the third set of parameters (single test)
        frame3 = ttk.Frame(container_frame, padding="10", name="frame3", borderwidth=2, relief="groove")
        frame3.grid(row=0, column=2, padx=10, pady=10)

        ttk.Label(frame3, text="Single Test Angle:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.single_test_angle_entry = ttk.Entry(frame3)
        self.single_test_angle_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame3, text="Single Test Accumulations:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.single_test_accumulations_entry = ttk.Entry(frame3)
        self.single_test_accumulations_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame3, text=" ExposTime (ms):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        self.single_test_exposure_time_entry = ttk.Entry(frame3)
        self.single_test_exposure_time_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame3, text="Move to Angle:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        self.move_to_angle_entry = ttk.Entry(frame3)
        self.move_to_angle_entry.grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(frame3, text="Go", command=lambda: self.motor_controller.move_to_angle(float(self.move_to_angle_entry.get()))).grid(row=3, column=2, padx=(5, 5), pady=5)

        # Create a horizontal frame for buttons and progress bar (2:1 ratio)
        button_frame = ttk.Frame(self.root, padding="10", name="button_frame", borderwidth=2, relief="groove")
        button_frame.grid(row=2, column=0, columnspan=3, padx=5,pady=2)
        
        # Create a style to configure the button color
        style = ttk.Style()
        style.configure("Green.TButton", background="green")

        # Home button
        ttk.Button(button_frame, text="Home", command=self.motor_controller.move_home,style="Green.TButton").grid(row=0, column=0, padx=(5, 5), pady=5)

        # Start Measurement button

        ttk.Button(button_frame, text="Start Measurement", command=self.start_measurement_thread).grid(row=0, column=1, padx=(5, 5), pady=5)

        # Progress bar
        ttk.Label(button_frame, text="Progress:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        self.progress_label = ttk.Label(button_frame, text="0%")
        self.progress_label.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.progress_bar = ttk.Progressbar(button_frame, orient='horizontal', length=130, mode='determinate')
        self.progress_bar.grid(row=0, column=4, padx=(0, 5), pady=5)  # Adjusted the padx to shift the progress bar to the left

        # Create a style to configure the button color
        style = ttk.Style()
        style.configure("Red.TButton", background="red")
        # Quit button
        ttk.Button(button_frame, text="Quit", command=self.quit_application,style="Red.TButton").grid(row=0, column=6, padx=(5, 5), pady=5)
        # Bind the close button to the quit_application method
        self.root.protocol("WM_DELETE_WINDOW", self.quit_application)

        # Button for performing a single test
        ttk.Button(button_frame, text="Single Test", command=self.perform_single_test).grid(row=0, column=5, pady=5)

        # Create a frame for angle adjustment
        angle_adjust_frame = ttk.Frame(self.root, padding="10", name="angle_adjust_frame", borderwidth=2, relief="groove")
        angle_adjust_frame.grid(row=2, column=3, pady=2)

        ttk.Label(angle_adjust_frame, text="Jog:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.angle_size_entry = ttk.Entry(angle_adjust_frame)
        self.angle_size_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(angle_adjust_frame, text="+", command=self.up_angle).grid(row=0, column=2, padx=(5, 5), pady=5)
        ttk.Button(angle_adjust_frame, text="-", command=self.down_angle).grid(row=0, column=3, padx=(5, 5), pady=5)

       # Create a figure and axes to display the plot
        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=4, column=0, columnspan=3, pady=10)  # Adjusted columnspan to 3

        # Create a frame for displaying current velocity and angle
        current_info_frame = ttk.Frame(self.root, padding="10", name="current_info_frame", borderwidth=2, relief="groove")
        current_info_frame.grid(row=4, column=2, pady=2, columnspan=1, sticky=tk.W)  # Adjusted column and columnspan

        ttk.Label(current_info_frame, text="Current Velocity:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.current_velocity_label = ttk.Label(current_info_frame, text="0 deg/s")
        self.current_velocity_label.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(current_info_frame, text="Current Accleration:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        self.current_velocity_label = ttk.Label(current_info_frame, text="0 deg/s^2")
        self.current_velocity_label.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(current_info_frame, text="Current Angle:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.current_angle_label = ttk.Label(current_info_frame, text="0 degrees")
        self.current_angle_label.grid(row=1, column=1, padx=5, pady=5)


    def update_current_info(self):
    # Method to update the current velocity and angle labels
        current_velocity = self.motor_controller.inst._get_velocity_max()
        current_angle = self.motor_controller.inst.position()
        current_acceleration = self.motor_controller.inst._get_velocity_acceleration()

        # self.current_velocity_label.config(text=f"{current_velocity:.2f} deg/s")
        self.current_angle_label.config(text=f"{current_angle:.2f} degrees")
        self.current_velocity_label.config(text=f"{current_acceleration:.2f} deg/s^2")

        # Schedule the update after a short delay
        self.root.after(500, self.update_current_info)

    def up_angle(self):
        # Implement the logic for increasing the angle
        if hasattr(self.motor_controller.inst, 'velocity_max'):
            self.motor_controller.inst.velocity_max(0)  # Set velocity to 0 before cleanup
        self.motor_controller.inst.velocity_max(25)
        current_angle = self.motor_controller.inst.position()
        angle_size = float(self.angle_size_entry.get())
        new_angle = (current_angle + angle_size) % 360  # Ensure the angle stays within [0, 360)
        self.motor_controller.move_to_angle(new_angle)

    def down_angle(self):
        # Implement the logic for decreasing the angle
        if hasattr(self.motor_controller.inst, 'velocity_max'):
            self.motor_controller.inst.velocity_max(0)  # Set velocity to 0 before cleanup
        self.motor_controller.inst.velocity_max(25)
        current_angle = self.motor_controller.inst.position()
        angle_size = float(self.angle_size_entry.get())
        new_angle = (current_angle - angle_size) % 360  # Ensure the angle stays within [0, 360)
        self.motor_controller.move_to_angle(new_angle)
    
    def home_angle(self):
        # Implement the logic for moving the angle to 0
        if hasattr(self.motor_controller.inst, 'velocity_max'):
            self.motor_controller.inst.velocity_max(0)
        self.motor_controller.inst.velocity_max(25)
        self.motor_controller.move_to_angle(0)

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
            exposure_time_mili= float(self.exposure_time_entry.get())
            exposure_time_micros = exposure_time_mili * 1000.0

            target_velocity = float(self.target_velocity_entry.get())
            experiment_name = self.experiment_name_entry.get()

            # Configure motor
            self.motor_controller.configure_motor(target_velocity=target_velocity)

            # Create measurement controller
            measurement_controller = MeasurementController(self.spectrometer_controller, self.motor_controller,experiment_name)

            # Clear previous plot
            self.ax.clear()

            # Measure at angles with default velocity using a while loop
            total_steps = ((final_angle - initial_angle) / step_size) + 1
            current_step = 1

            while current_step <= total_steps:
                angle = (initial_angle + (current_step - 1) * step_size)
                
                measurement_controller.measure_at_angles(
                    angle, angle, 1, num_accumulations, exposure_time_micros, 0.5
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
            # self.initial_angle_entry.delete(0, tk.END)
            # self.final_angle_entry.delete(0, tk.END)
            # self.step_size_entry.delete(0, tk.END)
            # self.target_velocity_entry.delete(0, tk.END)
            self.exposure_time_entry.delete(0, tk.END)
            self.num_accumulations_entry.delete(0, tk.END)

            # Check the checkbox state
            if self.go_home_var.get():
                # Go Home if the checkbox is checked\
                
                self.motor_controller.move_to_angle(0)

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
            single_test_exposure_time_mili = float(self.single_test_exposure_time_entry.get())
            single_test_exposure_time_micros = single_test_exposure_time_mili * 1000.0

            # Create measurement controller
            measurement_controller = MeasurementController(self.spectrometer_controller, self.motor_controller)

            # Clear previous plot
            self.ax.clear()

            # Perform a single test at the specified angle
            measurement_controller.measure_at_angles(
                single_test_angle, single_test_angle, 1, single_test_accumulations, single_test_exposure_time_micros,0.5
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
