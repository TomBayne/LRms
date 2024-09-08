"""
Handles connecting to the LoRa device via serial.

All this needs to do is:
- Connect to the device via serial and return a useable connection object.
- Send data on the serial connection.
- Read data from the serial connection.

Anything more should be done by another module.
"""

import serial

class Serial:
    """
    Manages a Serial connection and communication with the LoRa device.

    This class handles the serial connection, device configuration, and
    basic read/write operations for RYLR993 or RYLR998 LoRa modules.

    Attributes:
        conn (serial.Serial): Serial connection object.
        device_type (str): Type of the LoRa device ('RYLR993' or 'RYLR998').
        rf_freq (int): Radio frequency in Hz.
        node_id (int): Node ID for the device.
        tx_power (int): Transmission power in dBm.
        lora_params (str): LoRa parameters string.
    """

    def __init__(self, port='/dev/ttyS0', rf_freq=867500000, node_id=1, tx_power=22, lora_params='9,7,1,12', device_type='RYLR993'):
        """
        Initialise the DeviceConnection, creating a serial connection.

        Args:
            port (str): Serial port path.
            rf_freq (int): Radio frequency in Hz.
            node_id (int): Node ID for the device.
            tx_power (int): Transmission power in dBm.
            lora_params (str): LoRa parameters string.
            device_type (str): Type of the LoRa device ('RYLR993' or 'RYLR998').
        
        Raises:
            ValueError: If an invalid device type is provided.
        """
        if device_type not in ['RYLR993', 'RYLR998']:
            raise ValueError('Device type must be RYLR993 or RYLR998')
        baud_rates = {'RYLR993': 9600, 'RYLR998': 115200}
        self.conn = serial.Serial(port, baud_rates[device_type], timeout=1)
        self.device_type = device_type
        self.rf_freq = rf_freq
        self.node_id = node_id
        self.tx_power = tx_power
        self.lora_params = lora_params

    def read_serial(self, max_reads=100):
        """
        Read data from the serial connection.

        Args:
            max_reads (int): Maximum number of read attempts.

        Yields:
            str: Decoded data read from the serial connection.
        """
        for _ in range(max_reads):
            data = self.conn.readline().decode('utf-8').strip()
            if not data:
                break
            yield data

    def write_serial(self, text):
        """
        Write data to the serial connection.

        Args:
            text (str): Text to be written to the serial connection.
        """
        self.conn.write(text.encode())

    def close(self):
        """
        Close the serial connection to the device.
        """
        if self.conn.is_open:
            self.conn.close()
