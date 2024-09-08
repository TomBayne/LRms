"""
Describes a message object
A message object does not have a send() method because the message is sent via
whatever handles the connection to the device. This way the message object is agnostic
to however the device is connected. This will allow for more flexibility in the future.
"""

class Message:
    """
    Describes a message object
    """

    def __init__(self, content=b""):
        """
        Initialise the Message object.
        """
        self.content = content

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
        self.content = usr_text.encode()

    def decode(self):
        """
        Decodes the message from transmission.
        Eventually we should also decompress the message here.

        Returns:
            str: Decoded message string.
        """
        # TODO - Probably more to it than just decoding
        return self.content.decode()
