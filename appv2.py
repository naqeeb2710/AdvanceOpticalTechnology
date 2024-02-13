import tkinter as tk
from tkinter import ttk, IntVar
from threading import Thread
import sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import os
from main import SpectrometerController
from main import MotorController
from main import MeasurementController
import time
import csv
from liveSpectrum import LiveSpectrum as li
from tkinter import filedialog

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Amplified Spontaneous Emission Measurement App")

        # Initialize controllers
        # self.spectrometer_controller = SpectrometerController()
        self.motor_controller = MotorController()

        # Create IntVar to store checkbox state
        self.go_home_var = IntVar(value=1)  # Default to checked

        # Set up GUI components
        self.create_widgets()
        # self.update_current_info()

    def create_widgets(self):
        # Create a container frame for the layout
        container_frame = ttk.Frame(self.root, padding="5")
        container_frame.grid(row=0, column=0, padx=5, pady=5)

        # Create frame for the first set of parameters
        frame1 = ttk.Frame(container_frame, padding="5", name="frame1", borderwidth=2, relief="groove")
        frame1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(frame1, text="Initial Angle (degrees):").grid(row=0, column=0, padx=0, pady=0, sticky=tk.E)
        self.initial_angle_entry = ttk.Entry(frame1, width=10)  # Adjust the width as needed
        self.initial_angle_entry.grid(row=0, column=1, padx=0, pady=5)

        ttk.Label(frame1, text="Final Angle (degrees):").grid(row=0, column=2, padx=0, pady=0, sticky=tk.E)
        self.final_angle_entry = ttk.Entry(frame1,width=10)  # Adjust the width as needed
        self.final_angle_entry.grid(row=0, column=3, padx=0, pady=5)

        ttk.Label(frame1, text="Step Size (degrees):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        self.step_size_entry = ttk.Entry(frame1,width=10)
        self.step_size_entry.grid(row=2, column=1, padx=5, pady=5)

        # Create a checkbox for "Go Home" or "After Measurement" in frame2
        self.go_home_var = tk.IntVar()  # Define the variable
        self.go_home_checkbox = ttk.Checkbutton(frame1, text="Go Home After Measurement", variable=self.go_home_var)
        self.go_home_checkbox.grid(row=2, column=2, columnspan=2, pady=5, sticky=tk.W) 


        ttk.Label(frame1, text="Move to (degrees):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        self.move_to_angle_entry = ttk.Entry(frame1,width=10)
        self.move_to_angle_entry.grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(frame1, text="Go", command=self.moveangle).grid(row=3, column=2, padx=(5, 5), pady=5)

        ttk.Label(frame1, text="Jog (degrees):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.E)
        self.angle_size_entry = ttk.Entry(frame1,width=10)
        self.angle_size_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Button(frame1, text="+", command=self.up_angle).grid(row=4, column=2, padx=(5, 5), pady=5)
        ttk.Button(frame1, text="-", command=self.down_angle).grid(row=4, column=3, padx=(5, 5), pady=5)

        #create an input for experiment name
        # ttk.Label(frame1, text="Sample name:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        # self.experiment_name_entry = ttk.Entry(frame1)
        # self.experiment_name_entry.grid(row=3, column=1, padx=5, pady=5)

        # Create a frame for the second set of parameters
        frame2 = ttk.Frame(container_frame, padding="5", name="frame2", borderwidth=2, relief="groove")
        frame2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ttk.Label(frame2, text="Int. Time Spec (ms):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.exposure_time_entry = ttk.Entry(frame2,width=10)
        self.exposure_time_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame2, text="Num Accumulations:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.num_accumulations_entry = ttk.Entry(frame2,width=10)
        self.num_accumulations_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame2, text="Int. Time power(s)").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        self.int_time_power = ttk.Entry(frame2,width=10)
        self.int_time_power.grid(row=2, column=1, padx=5, pady=5)

        # # Create a checkbox for "Go Home" or "After Measurement" in frame2
        # self.go_home_var = tk.IntVar()  # Define the variable
        # self.go_home_checkbox = ttk.Checkbutton(frame2, text="Go Home After Measurement", variable=self.go_home_var)
        # self.go_home_checkbox.grid(row=3, column=0, columnspan=2, pady=5, sticky=tk.W) 

        # Progress bar
        ttk.Label(frame2, text="Progress:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.E)
        self.progress_label = ttk.Label(frame2, text="0%")
        self.progress_label.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)
        self.progress_bar = ttk.Progressbar(frame2, orient='horizontal', length=100, mode='determinate')
        self.progress_bar.grid(row=4, column=1, padx=(0, 10), pady=5)  # Adjusted the padx to shift the progress bar to the left

        # Create a frame for the third set of parameters (single test)
        frame3 = ttk.Frame(container_frame, padding="5", name="frame3", borderwidth=2, relief="groove")
        frame3.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        # ttk.Label(frame3, text="Move to Angle:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        # self.move_to_angle_entry = ttk.Entry(frame3)
        # self.move_to_angle_entry.grid(row=1, column=1, padx=5, pady=5)
        # ttk.Button(frame3, text="Go", command=self.moveangle).grid(row=1, column=2, padx=(5, 5), pady=5)
        ttk.Label(frame3, text="Sample name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.experiment_name_entry = ttk.Entry(frame3,width=10)
        self.experiment_name_entry.grid(row=0, column=1, padx=5, pady=5)


        ttk.Button(frame3, text="Live", command=self.live_spectrum).grid(row=1, column=0, pady=5)
        ttk.Button(frame3, text="Save Live", command=self.stop_live_spectrum).grid(row=1, column=1, padx=(5, 5), pady=5)

        # Start Measurement button
        ttk.Button(frame3, text="Take Spectrum", command=self.start_measurement).grid(row=2, column=0, padx=(5, 5), pady=5)

        ttk.Button(frame3, text=" Take Power", command=self.start_power_measurement).grid(row=2, column=1, padx=(5, 5), pady=5)

        # Create a style to configure the button color
        style = ttk.Style()
        style.configure("Green.TButton", background="green")
        # Home button
        ttk.Button(frame3, text="Home 0 Deg", command=self.motor_controller.move_home, style="Green.TButton").grid(row=3, column=0, padx=(5, 5), pady=5)
        
        # Create a style to configure the button color``
        style = ttk.Style()
        style.configure("Red.TButton", background="red")
        # Quit button
        ttk.Button(frame3, text="Exit", command=self.quit_application, style="Red.TButton").grid(row=3, column=1, padx=(5, 5), pady=5)
        # Bind the close button to the quit_application method
        self.root.protocol("WM_DELETE_WINDOW", self.quit_application)

        # Create a horizontal frame for buttons and progress bar (2:1 ratio)
        # button_frame = ttk.Frame(self.root, padding="5", name="button_frame", borderwidth=2, relief="groove")
        # button_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # # Create a style to configure the button color
        # style = ttk.Style()
        # style.configure("Green.TButton", background="green")

        # # Home button
        # ttk.Button(button_frame, text="Home", command=self.motor_controller.move_home, style="Green.TButton").grid(row=0, column=0, padx=(5, 5), pady=5)

        # # Start Measurement button
        # ttk.Button(button_frame, text="Spectrum", command=self.start_measurement).grid(row=0, column=1, padx=(5, 5), pady=5)

        # ttk.Button(button_frame, text="Power", command=self.start_power_measurement).grid(row=0, column=2, padx=(5, 5), pady=5)

        # # Progress bar
        # ttk.Label(button_frame, text="Progress:").grid(row=0, column=3, padx=5, pady=5, sticky=tk.E)
        # self.progress_label = ttk.Label(button_frame, text="0%")
        # self.progress_label.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        # self.progress_bar = ttk.Progressbar(button_frame, orient='horizontal', length=130, mode='determinate')
        # self.progress_bar.grid(row=0, column=5, padx=(0, 5), pady=5)  # Adjusted the padx to shift the progress bar to the left

        # # Create a style to configure the button color
        # style = ttk.Style()
        # style.configure("Red.TButton", background="red")
        # # Quit button
        # ttk.Button(button_frame, text="Quit", command=self.quit_application, style="Red.TButton").grid(row=0, column=6, padx=(5, 5), pady=5)
        # # Bind the close button to the quit_application method
        # self.root.protocol("WM_DELETE_WINDOW", self.quit_application)

        # ttk.Label(button_frame, text="Jog:").grid(row=0, column=7, padx=5, pady=5, sticky=tk.E)
        # self.angle_size_entry = ttk.Entry(button_frame)
        # self.angle_size_entry.grid(row=0, column=8, padx=5, pady=5)

        # ttk.Button(button_frame, text="+", command=self.up_angle).grid(row=0, column=9, padx=(5, 5), pady=5)
        # ttk.Button(button_frame, text="-", command=self.down_angle).grid(row=0, column=10, padx=(5, 5), pady=5)

        # Create a frame for displaying current velocity, acceleration, and angle
        current_info_frame = ttk.Frame(self.root, padding="10", name="current_info_frame", borderwidth=2, relief="groove")
        current_info_frame.grid(row=3, column=0, columnspan=3, pady=5, sticky="nsew")

        # Divide the frame into two columns: plot and info
        current_info_frame.grid_columnconfigure(0, weight=3)  # Plot column
        current_info_frame.grid_columnconfigure(1, weight=1)  # Info column

        # Create a figure and axes to display the plot
        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=current_info_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, pady=10, sticky="nsew")

        # Create a frame for the current info labels
        info_labels_frame = ttk.Frame(current_info_frame, padding="10")
        info_labels_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Create labels for current velocity, acceleration, and angle
        ttk.Label(info_labels_frame, text="Current Velocity:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.current_velocity_label = ttk.Label(info_labels_frame, text="0 deg/s")
        self.current_velocity_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(info_labels_frame, text="Current Acceleration:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.current_acceleration_label = ttk.Label(info_labels_frame, text="0 deg/s^2")
        self.current_acceleration_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(info_labels_frame, text="Current Angle:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.current_angle_label = ttk.Label(info_labels_frame, text="0 degrees")
        self.current_angle_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")


    def moveangle(self):
        # Implement the logic for moving to a specific angle
        angle = float(self.move_to_angle_entry.get())%360
        if hasattr(self.motor_controller.inst, 'velocity_max'):
            self.motor_controller.inst.velocity_max(0)  # Set velocity to 0 before cleanup
        self.motor_controller.inst.velocity_max(25)
        self.motor_controller.move_to_angle(angle)

    def update_current_info(self):
    # Method to update the current velocity and angle labels
        current_velocity = self.motor_controller.inst._get_velocity_max()
        current_angle = self.motor_controller.inst.position()
        current_acceleration = self.motor_controller.inst._get_velocity_acceleration()

        self.current_velocity_label.config(text=f"{current_velocity:.2f} deg/s")
        self.current_angle_label.config(text=f"{current_angle:.2f} degrees")
        self.current_acceleration_label.config(text=f"{current_acceleration:.2f} deg/s^2")


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
            self.spectrometer_controller = SpectrometerController()
            initial_angle = float(self.initial_angle_entry.get())
            step_size = float(self.step_size_entry.get())
            final_angle = float(self.final_angle_entry.get())
            num_accumulations = int(self.num_accumulations_entry.get())
            exposure_time_mili= float(self.exposure_time_entry.get())
            exposure_time_micros = exposure_time_mili * 1000.0

            # target_velocity = float(self.target_velocity_entry.get())
            experiment_name = self.experiment_name_entry.get()

            # Configure motor
            # self.motor_controller.configure_motor(25)

            # Create measurement controller
            measurement_controller = MeasurementController(self.spectrometer_controller, self.motor_controller,experiment_name)

            # Clear previous plot
            self.ax.clear()
            
            save_dir = filedialog.askdirectory()

            # Measure at angles with default velocity using a while loop
            total_steps = ((final_angle - initial_angle) / step_size) + 1
            current_step = 1

            while current_step <= total_steps:
                angle = (initial_angle + (current_step - 1) * step_size)
                
                measurement_controller.measure_at_angles(
                    angle, angle, 1, num_accumulations, exposure_time_micros, 0.5,save_dir
                )

                # Access the current_csv_filename from the MeasurementController
                current_csv_filename = measurement_controller.current_csv_filename
                # Dynamically generate the plot filename based on the current angle
                output_plot_filename = current_csv_filename.replace('.csv', '.png')
                # Save the plot as an image file in the "plot" folder
                output_plot_filepath = os.path.join(save_dir, output_plot_filename)
                print(f"Plot saved to: {output_plot_filepath}")

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
                
            # Check the checkbox state
            if self.go_home_var.get():
                # Go Home if the checkbox is checked\
                
                self.motor_controller.move_to_angle(0)
            self.spectrometer_controller.disconnect_spectrometer()

        except Exception as e:
            print(f"An error occurred: {e}")
            # Close motor and spectrometer in case of an error
            self.motor_controller.close_motor()
            self.spectrometer_controller.disconnect_spectrometer()
    
    def start_power_measurement(self):
        try:
            # Get user input values
            self.spectrometer_controller=SpectrometerController()
            initial_angle = float(self.initial_angle_entry.get())
            step_size = float(self.step_size_entry.get())
            final_angle = float(self.final_angle_entry.get())
            power_delay = float(self.int_time_power.get())
            
            # target_velocity = float(self.target_velocity_entry.get())
            experiment_name = self.experiment_name_entry.get()

            # Configure motor
            self.motor_controller.configure_motor(25)
            save_dir = filedialog.askdirectory()
            if not save_dir:
            # If the user cancels the dialog, return without saving
                return

            # Create measurement controller
            measurement_controller = MeasurementController(self.spectrometer_controller, self.motor_controller, experiment_name)

            # Clear previous plot
            self.ax.clear()

            angle_power_list = []  # Initialize an empty list to store angle-power pairs
            # dump_folder = 'experiment_data'
            # os.makedirs(dump_folder, exist_ok=True)
            measurement_range = measurement_controller.default_measurement_range  # Initialize measurement range
            status_counter = 0  # Initialize status counter
            measurement_controller.power_meter.connect()

            # Measure at angles with default velocity using a while loop
            current_angle = initial_angle
            while current_angle <= final_angle:
                angle = current_angle % 360  # Convert angle to be within the range [0, 360)
                measurement_controller.motor_controller.move_to_angle(angle)
                current_position = measurement_controller.motor_controller.inst.position()
                print(f"Position: {current_position} degrees at angle: {angle} degrees")
                time.sleep(0.5)  # Pause the execution for 0.5 seconds
                measurement_controller.power_meter.connect()
                measurement_controller.power_meter.arm(delay_seconds=power_delay)
                power_data, average_power = measurement_controller.power_meter.disarm()  # Unpack the tuple to get power data and average power
                if power_data:
                    print("Power data recorded:")
                    power_meter_filename = os.path.join(save_dir, f'{experiment_name}_power_{int(angle)}deg.csv')
                    with open(power_meter_filename, 'w') as power_dump:
                        # Write header
                        power_dump.write('time, power, status\n')
                        # Write data rows
                        for event in power_data:
                            power_dump.write('%.3f, %.2e, %.2f\n' % (event[0], event[1], event[2]))
                            if measurement_controller.power_meter.measurement_range == 3:  # Check if not already in 200nJ range
                                if event[2] == 1:  # Check if data indicates status change
                                    status_counter += 1
                                    print('status counter = ', status_counter)
                else:
                    print("No power data recorded.")
                
                # Check if status counter exceeds threshold
                if status_counter > measurement_controller.threshold_status_count:
                    measurement_range = 2  # Change to 200nJ range
                    measurement_controller.power_meter.measurement_range = measurement_range
                    status_counter = 0  # Reset status counter after changing the range
                    measurement_controller.power_meter.connect()
                    measurement_controller.power_meter.arm()
                    power_data, average_power = measurement_controller.power_meter.disarm()
                    if power_data:
                        print("Power data recorded:")
                        power_meter_filename = os.path.join(save_dir, f'{experiment_name}_power_{angle}deg.csv')
                        with open(power_meter_filename, 'w') as power_dump:
                            # Write header
                            power_dump.write('time, power, status\n')
                            # Write data rows
                            for event in power_data:
                                power_dump.write('%.3f, %.2e, %.2f\n' % (event[0], event[1], event[2]))
                else:
                    status_counter = 0  # Reset status counter if not exceeded threshold
                
                angle_power_list.append([angle, average_power])
                current_angle += step_size

            # Move to the final angle after completing the loop
            final_angle_normalized = final_angle % 360
            measurement_controller.motor_controller.move_to_angle(final_angle_normalized)
            final_position = measurement_controller.motor_controller.inst.position()
            print(f"Final Position: {final_position} degrees")
            print(angle_power_list)
            # Save the angle-power list to a CSV file
            os.makedirs('experiment_data', exist_ok=True)
            angle_power_filename = os.path.join(save_dir, f'{experiment_name}_angle_power.csv')
            with open(angle_power_filename, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                header = ['Angle (deg)', 'Average Power (nJ)']
                csv_writer.writerow(header)
                for row in angle_power_list:
                    csv_writer.writerow(row)
            print(">>>Angle vs plot data")

            self.spectrometer_controller.disconnect_spectrometer()
            angles, powers = zip(*angle_power_list)
            plt.figure(figsize=(12, 8))
            plt.scatter(angles, powers)
            plt.xlabel('Angle (deg)')
            plt.ylabel('Average Power (nJ)')
            plt.yticks([i for i in range(0, int(max(powers)) + 5, 5)])  # Set ticks at intervals of 5
            #save plot in experiment_data folder
            plot_filename = os.path.join(save_dir, f'{experiment_name}_angle_power.png')
            plt.savefig(plot_filename, bbox_inches='tight', pad_inches=0.5)
            print(">>>plot saved")
            # plt.savefig(f'/{experiment_name}_angle_power.png', bbox_inches='tight', pad_inches=0.5)

            # Display the latest graph in the Tkinter application
            img = plt.imread(plot_filename)
            # img = plt.imread(f'experiment_data/{experiment_name}_angle_power.png')
            self.ax.imshow(img)
            self.ax.axis('off')  # Turn off axis labels
            # Update the canvas
            self.canvas.draw()

            # Clear input fields after the calculation
            # self.initial_angle_entry.delete(0, tk.END)

            # Check the checkbox state
            if self.go_home_var.get():
                # Go Home if the checkbox is checked
                measurement_controller.motor_controller.move_to_angle(0)

        except Exception as e:
            print(f"An error occurred: {e}")
            # Close motor and spectrometer in case of an error
            self.motor_controller.close_motor()
            self.spectrometer_controller.disconnect_spectrometer()
                       
    def live_spectrum(self):
        try:
            print("Live spectrum started")
            self.liveSpec = li()
            # print("object created")
            exposure_time_entry_value = self.exposure_time_entry.get()
            exposure_time_mili = float(exposure_time_entry_value)
            exposure_time_micros = exposure_time_mili * 1000.0
            for plot_path in self.liveSpec.live_spectrum(exposure_time_micros, max_plots=5):
                # Load the plot image
                img = plt.imread(plot_path)
                # print("Latest plot path:", plot_path)
                # Display the plot image in the Tkinter application
                self.ax.imshow(img)
                self.ax.axis('off')
                self.canvas.draw()
                 # Adjust the delay time as needed
                self.root.after(2, self.root.update())
            
        except Exception as e:
            print(f"An error occurred: {e}")
            self.liveSpec.close()
            # self.motor_controller.close_motor()
            # self.liveSpec.close_plot()
            
    
    def stop_live_spectrum(self):
        # Set the flag to stop the live spectrum
        exposure_time_entry_value = self.exposure_time_entry.get()
        exposure_time_mili = float(exposure_time_entry_value)
        exposure_time_micros = exposure_time_mili * 1000.0

        self.liveSpec.save_live_spectrum(exposure_time_micros)


    def quit_application(self):
        # Disconnect spectrometer and close motor when quitting the application
        # self.spectrometer_controller.disconnect_spectrometer()
        self.motor_controller.close_motor()
        self.root.quit()
        self.root.destroy()
        sys.exit()

# Create the main application window
root = tk.Tk()
app = App(root)
root.mainloop()
