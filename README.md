# Basler Camera Hardware Trigger Setup

This guide provides step-by-step instructions for setting up and running Basler cameras with a hardware trigger for synchronized recording. Please follow these guidelines carefully to ensure a successful setup.

## Prerequisites

Before you begin, make sure you have the following prerequisites:

- **Basler Cameras:** Ensure that you have the Basler cameras you intend to use with the hardware trigger.
- **Hardware Trigger:** You should have the hardware trigger device.
- **USB 3.1 Port:** Your laptop or computer must have USB 3.1 ports to connect the cameras.

## Hardware Trigger Setup

1. **Connect Cameras:** Connect the Basler cameras to the hardware trigger using the provided cables. Pay attention to the color-coding on the hardware trigger to identify where to plug in each cable. You will have a blue and white pin, and the hardware trigger should indicate where each cable goes.

2. **Configure Trigger Settings:**
   - **Frequency (FREQ):** Adjust the frequency setting as needed. The maximum synchronization frequency is 150-155 frames per second (fps).
   - **Duty Cycle (DUTY):** Keep the duty cycle between 10% and 30% for optimal performance.

## Software Setup

### 1. Create a Conda Environment

Follow these steps to create a Conda environment for running the code:

```bash
# Create a new Conda environment (replace 'myenv' with your preferred environment name)
conda create --name myenv python=3.8

# Activate the newly created environment
conda activate myenv
```

## Install Requirements

After creating and activating your Conda environment, install the required Python packages by providing a requirements.txt file. Ensure you have the requirements.txt file available in your project directory. You can install the requirements using pip as follows:

```bash
pip install -r requirements.txt
```

## Starting the Code
- Run the Code: After completing the installation and camera connection, you can now start the Python code to control and record from the connected Basler cameras. Make sure to start the code in the Conda environment you created earlier.

```bash
python main.py
```

- Connect the USB Trigger: While the code is running, plug in the USB trigger into a laptop or a power source. This action will trigger the cameras to start recording simultaneously, in sync with the configured hardware trigger settings.

# Debugging
flask --app main.py --debug run
