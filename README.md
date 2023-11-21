# Thorlabs K10CR1 and Spectrometer Automation Setup

## Introduction
Welcome to the Thorlabs K10CR1 and Spectrometer Automation setup guide. This guide is designed to help you set up a GUI application using Tkinter for experiment automation. The application allows you to specify the start angle, final angle, step size, exposure time, and the number of accumulations for a Thorlabs K10CR1 rotation stage. The spectrometer collects data at each angle, providing a seamless solution for your experimental needs.

The application automatically saves the collected data in CSV files within the "data" folder. Additionally, the generated plots are stored in the "plot" folder. You can also view the live plot on the GUI during the experiment.


## Thorlabs K10CR1 Requirements
1. **Download APT Software:**
   - Download and install the APT (Advanced Positioning Technology) software from Thorlabs.
   - [Thorlabs Software](https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=Motion_Control).

2. **Install QCoDeS Contrib Drivers:**
   - Install the QCoDeS Contrib Drivers package:
     ```
     pip install qcodes_contrib_drivers
     ```

## Ocean Optics Spectrometer Setup

1. **Install Spectra Suite:**
   - Download and install [Spectra Suite](https://digital.lib.washington.edu/researchworks/bitstream/handle/1773/37113/Appendix%20D%20-%20HR4000.pdf?sequence=5) for Ocean Optics spectrometers.

2. **Install Python Seabreeze:**
   - Install the Python Seabreeze package:
     ```
     pip install seabreeze
     ```

## How to Run the Application

1. **Open Terminal:**
   - Open a terminal window on your computer.

2. **Navigate to the Application Folder:**
   - Use the `cd` command to navigate to the folder where your application is located.

3. **Run the Application:**
   - Type the following command and press Enter to run the application:
     ```
     python application.py
     ```

4. **GUI Interface:**
   - The GUI application will open, providing a user-friendly interface for experiment automation.

5. **Enter Required Fields:**
   - Enter the required parameters, such as the start angle, final angle, step size, exposure time, and the number of accumulations.

## Addtional Resoures

1. **Learn More About QCoDeS Contrib Drivers:**
   - [QCoDeS Contrib Drivers Documentation](https://qcodes.github.io/Qcodes_contrib_drivers/index.html).

2. **Explore Thorlabs K10CR1 Example:**
   - [Thorlabs K10CR1 Example](https://qcodes.github.io/Qcodes_contrib_drivers/examples/Thorlabs_K10CR1.html).

3. **Read Python Seabreeze Documentation:**
   - [Python Seabreeze Documentation](https://python-seabreeze.readthedocs.io/en/latest/).


