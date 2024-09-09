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

    def __init__(self, content: str = ""):
        """
        Initialise the Message object.
        """
        self.content = content.encode()

    def encode(self):
        """
        Encodes the current message content for transmission.
        Eventually we should also compress the message here.
        """
        if isinstance(self.content, str):
            self.content = self.content.encode()
        elif isinstance(self.content, bytes):
            raise TypeError("Attempted to encode an already encoded message.")

    def decode(self):
        """
        Decodes the message in the contents buffer..
        Eventually we should also decompress the message here.

        Returns:
            str: Decoded message string.
        """
        # TODO - Probably more to it than just decoding
        if isinstance(self.content, bytes):
            self.content = self.content.decode()
        elif isinstance(self.content, str):
            raise TypeError("Attempted to decode a plaintext message.")
