"""
Handles initial configuration of a supported LoRa device.

This won't use the device_commands module, because it's just for initial setup.
Instead we will just write the raw commands to the serial connection.
"""

from time import sleep
from .device_connection import Serial


class DeviceConfigurator:
    """
    Manages the configuration of the LoRa device.

    The configuration processes defined here are not nice but I wanted to keep it obvious
    exactly what the confugration process is.
    """

    def __init__(self, connection: Serial, rf_freq: int, node_id: int, tx_power: int, lora_params: str):
        """
        Initialise the DeviceConfigurator.

        Args:
            connection (DeviceConnection): The device connection object.
            rf_freq (int): Radio frequency in Hz.
            node_id (int): Node ID for the device.
            tx_power (int): Transmission power in dBm.
            lora_params (str): LoRa parameters string.
        """
        self.connection = connection
        self.rf_freq = rf_freq
        self.node_id = node_id
        self.tx_power = tx_power
        self.lora_params = lora_params

    def configure_rylr993(self):
        """
        Configure a RYLR993 with the specified settings.

        This method sends a series of AT commands to set up the device
        according to the initialised parameters.
        """
        setup_cmds = ['AT+RESET\r\n', 'AT+OPMODE=1\r\n', 'AT+RESET\r\n', f'AT+BAND={self.rf_freq}\r\n',
                      f'AT+ADDRESS={self.node_id}\r\n', f'AT+CRFOP={self.tx_power}\r\n', f'AT+PARAMETER={self.lora_params}\r\n']
        for cmd in setup_cmds:
            self.connection.write_serial(cmd)
            sleep(2)
        self.connection.read_serial()

    def configure_rylr998(self):
        """
        Configure a RYLR998 with the specified settings.

        This method sends a series of AT commands to set up the device
        according to the initialised parameters.
        """
        setup_cmds = ['AT+RESET\r\n', f'AT+BAND={self.rf_freq}\r\n', f'AT+ADDRESS={self.node_id}\r\n',
                      f'AT+CRFOP={self.tx_power}\r\n', f'AT+PARAMETER={self.lora_params}\r\n']
        for cmd in setup_cmds:
            self.connection.write_serial(cmd)
            sleep(2)
        self.connection.read_serial()
