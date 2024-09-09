"""
Main entry point for the Beacon Master application.
"""

import sys
from src.functions.device_connection import Serial
from src.functions.device_setup import DeviceConfigurator


def run_ui(conn):
    """
    TODO: Unimplemented.
    Main function which runs the application.
    """
    return


def connect(device_type):
    """
    Connect to the specified LoRa device and configure.

    Args:
        device_type (str): Type of the LoRa device ('RYLR993' or 'RYLR998').

    Returns:
        DeviceConnection: The device connection object.
    """
    conn = Serial(device_type=device_type)
    device_configurator = DeviceConfigurator(
        conn, 867500000, 1, 22, '9,7,1,12')
    if device_type == 'RYLR993':
        device_configurator.configure_rylr993()
    elif device_type == 'RYLR998':
        device_configurator.configure_rylr998()
    else:
        raise ValueError(f"Invalid device type: {device_type}")
    return conn


if __name__ == '__main__':
    # Simple connection UI, will improve later.
    usr_in = input("Select model:\n1. RYLR993\n2. RYLR998\n")
    if usr_in == '1':
        device_connection = connect('RYLR993')
    elif usr_in == '2':
        device_connection = connect('RYLR998')
    else:
        raise ValueError('Invalid input')
    run_ui(device_connection)

    print("Exiting program...")
    device_connection.close()
    sys.exit(0)
