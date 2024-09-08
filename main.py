"""
Main entry point for the Beacon Master application.
"""

from serial import SerialException
from src.functions.device_connection import DeviceConnection
from src.functions.device_setup import DeviceConfigurator
from src.functions.commander import Commander
from src.ui import BeaconMasterUI

def run_ui(stdscr, device_connection, commander):
    """
    Main function to set up and run the application.

    Args:
        stdscr (curses.window): The main curses window.
    """
    try:
        commander = Commander(device_connection)
        ui = BeaconMasterUI(stdscr, device_connection, commander)
        ui.run()
    except SerialException as e:
        stdscr.addstr(0, 0, f"Serial Error: {e}")
        stdscr.refresh()
        stdscr.getch()

def connect(device_type):
    """
    Connect to the specified LoRa device and configure.

    Args:
        device_type (str): Type of the LoRa device ('RYLR993' or 'RYLR998').

    Returns:
        DeviceConnection: The device connection object.
    """
    device_connection = DeviceConnection(device_type=device_type)
    device_configurator = DeviceConfigurator(device_connection, 867500000, 1, 22, '9,7,1,12')
    if device_type == 'RYLR993':
        device_configurator.configure_rylr993()
    elif device_type == 'RYLR998':
        device_configurator.configure_rylr998()
    else:
        raise ValueError(f"Invalid device type: {device_type}")
    return device_connection
