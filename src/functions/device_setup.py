"""
Handles initial configuration of a supported LoRa device.
"""

import threading

class DeviceConfigurator:
    """
    Manages the configuration of the LoRa device.
    """
    def __init__(self, connection, rf_freq, node_id, tx_power, lora_params):
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
        self.connection.write_serial('AT+RESET\r\n')
        threading.Event().wait(2)
        self.connection.write_serial('AT+OPMODE=1\r\n')
        threading.Event().wait(2)
        self.connection.write_serial('AT+RESET\r\n')
        threading.Event().wait(2)
        self.connection.write_serial(f'AT+BAND={self.rf_freq}\r\n')
        threading.Event().wait(1)
        self.connection.write_serial(f'AT+ADDRESS={self.node_id}\r\n')
        threading.Event().wait(1)
        self.connection.write_serial(f'AT+CRFOP={self.tx_power}\r\n')
        threading.Event().wait(1)
        self.connection.write_serial(f'AT+PARAMETER={self.lora_params}\r\n')
        threading.Event().wait(1)
        self.connection.read_serial()

    def configure_rylr998(self):
        """
        Configure a RYLR998 with the specified settings.

        This method sends a series of AT commands to set up the device
        according to the initialised parameters.
        """
        self.connection.write_serial('AT+RESET\r\n')
        threading.Event().wait(2)
        self.connection.write_serial(f'AT+BAND={self.rf_freq}\r\n')
        threading.Event().wait(1)
        self.connection.write_serial(f'AT+ADDRESS={self.node_id}\r\n')
        threading.Event().wait(1)
        self.connection.write_serial(f'AT+CRFOP={self.tx_power}\r\n')
        threading.Event().wait(1)
        self.connection.write_serial(f'AT+PARAMETER={self.lora_params}\r\n')
        threading.Event().wait(1)
        self.connection.read_serial()
