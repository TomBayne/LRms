"""
A more sophisticated and pythonic version of the LRms-repeater-pico.py script.
Aiming for a modular design and easier to add to down the road.
"""

import time
import machine
from machine import Pin


class DeviceConnection:
    """
    Manages the connection and communication with the LoRa device.
    This class handles the UART connection, device configuration, and
    basic read/write operations for RYLR993 or RYLR998 LoRa modules.

    Attributes:
        uart (machine.UART): UART connection object.
        device_type (str): Type of the LoRa device ('RYLR993' or 'RYLR998').
        rf_freq (int): Radio frequency in Hz.
        node_id (int): Node ID for the device.
        tx_power (int): Transmission power in dBm.
        lora_params (str): LoRa parameters string.
    """

    def __init__(self, tx_pin=0, rx_pin=1, rf_freq=867500000, node_id=100, tx_power=22, lora_params='9,7,1,12', device_type='RYLR993'):
        """
        Initialize the DeviceConnection.

        Args:
            tx_pin (int): TX pin number.
            rx_pin (int): RX pin number.
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
        self.uart = machine.UART(0, baudrate=baud_rates[device_type], tx=machine.Pin(
            tx_pin), rx=machine.Pin(rx_pin))
        self.device_type = device_type
        self.rf_freq = rf_freq
        self.node_id = node_id
        self.tx_power = tx_power
        self.lora_params = lora_params

    def read_serial(self, timeout=5000):
        """
        Read data from the UART connection.

        Args:
            timeout (int): Timeout in milliseconds.

        Returns:
            bytes: Data read from the UART connection.
        """
        start_time = time.time.ticks_ms()
        received_data = b''
        while not received_data.endswith(b'\r\n'):
            if time.time.ticks_diff(time.time.ticks_ms(), start_time) > timeout:
                break
            new_data = self.uart.read()
            if new_data:
                received_data += new_data
        return received_data

    def write_serial(self, text):
        """
        Write data to the UART connection.

        Args:
            text (str): Text to be written to the UART connection.
        """
        self.uart.write(text.encode())

    def configure_device(self):
        """
        Configure the LoRa device with the specified settings.
        This method sends a series of AT commands to set up the device
        according to the initialized parameters.
        """
        self.write_serial('AT+RESET\r\n')
        time.sleep(2)

        if self.device_type == 'RYLR993':
            self.write_serial('AT+OPMODE=1\r\n')
            time.sleep(2)

        self.write_serial('AT+RESET\r\n')
        time.sleep(2)

        self.write_serial(f'AT+BAND={self.rf_freq}\r\n')
        time.sleep(1)

        self.write_serial(f'AT+ADDRESS={self.node_id}\r\n')
        time.sleep(1)

        self.write_serial(f'AT+CRFOP={self.tx_power}\r\n')
        time.sleep(1)

        self.write_serial(f'AT+PARAMETER={self.lora_params}\r\n')
        time.sleep(1)

        for _ in range(10):  # Read and discard any responses
            self.uart.readline()


class MessageHandler:
    """
    Handles message operations for the LoRa device.
    This class is responsible for processing received messages and
    sending repeated messages.

    Attributes:
        device_connection (DeviceConnection): The device connection object.
        station_id (str): The ID of this station.
    """

    def __init__(self, device_connection, station_id):
        """
        Initialize the MessageHandler.

        Args:
            device_connection (DeviceConnection): The device connection object.
            station_id (str): The ID of this station.
        """
        self.device_connection = device_connection
        self.station_id = station_id

    def process_message(self, received_data):
        """
        Process the received message and repeat if necessary.

        Args:
            received_data (bytes): The received data.

        Returns:
            str: A string describing the action taken.
        """
        if b"RPT" in received_data:
            return "Ignoring repeated message"

        decoded_data = received_data.decode().strip()
        if "+RCV=" not in decoded_data:
            return f"Received non-message data: {decoded_data}"

        parts = decoded_data.split(",")
        if len(parts) < 3:
            return f"Received malformed message: {decoded_data}"

        sender_id = parts[0].split("=")[1]
        message_text = parts[2].strip()

        total_chars = len(message_text) + len(sender_id) + \
            len(" VIA") + len(self.station_id)
        repeated_message = f"AT+SEND=0,{total_chars},{
            message_text} {sender_id}VIA{self.station_id}\r\n"

        self.device_connection.write_serial(repeated_message)
        return f"Repeated message: {repeated_message.strip()}"


class RepeaterApplication:
    """
    Main application class for the LRms Repeater.
    This class sets up the device connection, message handler, and
    runs the main application loop.

    Attributes:
        device_connection (DeviceConnection): The device connection object.
        message_handler (MessageHandler): The message handler object.
        led (machine.Pin): LED pin object.
    """

    def __init__(self, led_pin=25):
        """
        Initialize the RepeaterApplication.

        Args:
            led_pin (int): Pin number for the LED.
        """
        self.device_connection = DeviceConnection()
        self.message_handler = MessageHandler(self.device_connection, "100")
        self.led = Pin(led_pin, Pin.OUT)

    def setup(self):
        """
        Set up the device connection and LED.
        """
        self.device_connection.configure_device()
        self.led.value(1)

    def run(self):
        """
        Run the main application loop.
        """
        print("LRms Repeater running. Press Ctrl+C to stop.")
        try:
            while True:
                received_data = self.device_connection.read_serial()
                if received_data:
                    print(f"Received: {received_data.decode().strip()}")
                    result = self.message_handler.process_message(
                        received_data)
                    print(result)
                    self.blink_led()
        except KeyboardInterrupt:
            print("Repeater stopped.")

    def blink_led(self):
        """
        Blink the LED to indicate message processing.
        """
        self.led.value(1)
        time.sleep(0.5)
        self.led.value(0)


def main():
    """
    Main function to set up and run the application.
    """
    app = RepeaterApplication()
    app.setup()
    app.run()


if __name__ == "__main__":
    main()
