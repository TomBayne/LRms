"""
Defines how specific commands should be formatted to be sent to the LoRa device.
Does not send the commands, only creates them as an object.

- RST: Reset the LoRa device.
- AT: Send an AT command to the LoRa device.
- SEND: Send a message to the LoRa device.
"""

from .message import Message
from .device_connection import Serial


class Command:
    """
    Defines how specific commands should be formatted to be sent to the LoRa device.

    - RST: Reset the LoRa device.   
    - AT: Send an AT command to the LoRa device.
    - SEND: Send a message to the LoRa device.
    """

    def __init__(self, connection: Serial):
        """
        Initialise the Command object.

        Arguments:
            connection (DeviceConnection): The device connection object.
        """
        self.connection = connection

    def send_msg(self, message: Message):
        """
        Takes a message object, prepares it, and sends it to over RF via the serial device.

        Arguments:
            message (Message): The message object to send.
        """
        msg_bytes = message.encode()
        prepared = f"AT+SEND=0,{len(msg_bytes)},{msg_bytes}\r\n"
        self.connection.write_serial(prepared.encode())

    def reset(self):
        """
        Resets the LoRa device.
        """
        self.connection.write_serial(b"AT+RST\r\n")

    def custom_at_cmd(self, command: str):
        """
        Sends a custom ATcommand to the LoRa device.

        Arguments:
            command (str): The command to send (Without the 'AT+').
        """
        self.connection.write_serial(f"AT+{command}\r\n".encode())
