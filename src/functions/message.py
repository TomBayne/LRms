"""
Describes a message object
"""

class Message:
    """
    Describes a message object
    """

    def __init__(self, msg_bytes=b""):
        """
        Initialise the Message object.
        """
        self.msg_bytes = msg_bytes

    def send(self):
        """
        Sends a message via the serial connection.

        Returns:
            bool: True if the message was sent successfully, False otherwise.
        """
        # TODO
        return False

    def encode(self, usr_text):
        """
        Encodes the message for transmission and places it in the bytes buffer.
        Eventually we should also compress the message here.

        Args:
            usr_text (str): String to encode
        Returns:
            str: Encoded message string.
        """
        # TODO - Probably more to it than just encoding, e.g. Headers.
        self.msg_bytes = usr_text.encode()

    def decode(self):
        """
        Decodes the message from transmission.
        Eventually we should also decompress the message here.

        Returns:
            str: Decoded message string.
        """
        # TODO - Probably more to it than just decoding
        return self.msg_bytes.decode()
