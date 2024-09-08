"""
Handles command operations for the LoRa device.
"""

class Commander:
    """
    Handles command operations for the LoRa device.

    This class is responsible for sending AT commands and managing
    beacon transmissions.

    Attributes:
        device_connection (DeviceConnection): The device connection object.
    """

    def __init__(self, device_connection):
        """
        Initialise the Commander.

        Args:
            device_connection (DeviceConnection): The device connection object.
        """
        self.device_connection = device_connection

    def send_at_command(self, command):
        """
        Send an AT command to the LoRa device.

        Args:
            command (str): The command to send.

        Returns:
            str: A string describing the sent command.
        """
        cmd_length = len(command)
        full_command = f"AT+SEND=0,{cmd_length},{command}\r\n"
        self.device_connection.write_serial(full_command)
        return f"Sent command: {full_command.strip()}"
