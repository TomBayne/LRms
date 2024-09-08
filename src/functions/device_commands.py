"""
Defines how specific commands should be formatted to be sent to the LoRa device.
Does not send the commands, only creates them as an object.

- RST: Reset the LoRa device.
- AT: Send an AT command to the LoRa device.
- SEND: Send a message to the LoRa device.
- REC: Receive a message from the LoRa device.

TODO: I'm not sure yet if these commands are even correct, or what we need. It's just a placeholder.
"""

class Command:
    """
    Defines how specific commands should be formatted to be sent to the LoRa device.

    - RST: Reset the LoRa device.   
    - AT: Send an AT command to the LoRa device.
    - SEND: Send a message to the LoRa device.
    - REC: Receive a message from the LoRa device.
    """

    def __init__(self, command_content=''):
        """
        Initialise the Command object.

        Args:
            command_type (str): The type of command to send ('RST', 'AT', 'SEND', 'REC').
            command (str): The command to send.
        """
        self.command_content = command_content

    def rst(self):
        """
        Build and send a reset command to the LoRa device.

        Returns:
            str: A string describing the sent command.
        """
        return "AT+RESET\r\n"

    def at(self):
        """
        Build and send an AT command to the LoRa device.

        Returns:
            str: A string describing the sent command.
        """
        return f"AT{self.command_content}\r\n"
    
    def send(self):
        """
        Build and send a SEND command to the LoRa device.

        Returns:
            str: A string describing the sent command.
        """
        return f"SEND {self.command_content}\r\n"

    def rec(self):
        """
        Build and send a REC command to the LoRa device.

        Returns:
            str: A string describing the sent command.
        """
        return f"REC {self.command_content}\r\n"