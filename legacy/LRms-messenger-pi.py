"""
A more sophisticated and pythonic version of the LRms-messenger-pi.py script.
Aiming for a modular design and easier to add to down the road.
"""


from datetime import datetime
from collections import deque
import threading
import serial
import RPi.GPIO as GPIO


class DeviceConnection:
    """
    Manages the connection and communication with the LoRa device.
    This class handles the serial connection, device configuration, and
    basic read/write operations for RYLR993 or RYLR998 LoRa modules.

    Attributes:
        uart (serial.Serial): Serial connection object.
        device_type (str): Type of the LoRa device ('RYLR993' or 'RYLR998').
        rf_freq (int): Radio frequency in Hz.
        node_id (int): Node ID for the device.
        tx_power (int): Transmission power in dBm.
        lora_params (str): LoRa parameters string.
    """

    def __init__(self, port='/dev/ttyS0', rf_freq=867500000, node_id=1, tx_power=22, lora_params='9,7,1,12', device_type='RYLR993'):
        """
        Initialize the DeviceConnection.

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
        self.uart = serial.Serial(port, baud_rates[device_type], timeout=1)
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
            data = self.uart.readline().decode('utf-8').strip()
            if not data:
                break
            yield data

    def write_serial(self, text):
        """
        Write data to the serial connection.

        Args:
            text (str): Text to be written to the serial connection.
        """
        self.uart.write(text.encode())

    def configure_device(self):
        """
        Configure the LoRa device with the specified settings.
        This method sends a series of AT commands to set up the device
        according to the initialized parameters.
        """
        self.write_serial('AT+RESET\r\n')
        threading.Event().wait(2)

        if self.device_type == 'RYLR993':
            self.write_serial('AT+OPMODE=1\r\n')
            threading.Event().wait(2)

        self.write_serial('AT+RESET\r\n')
        threading.Event().wait(2)

        self.write_serial(f'AT+BAND={self.rf_freq}\r\n')
        threading.Event().wait(1)

        self.write_serial(f'AT+ADDRESS={self.node_id}\r\n')
        threading.Event().wait(1)

        self.write_serial(f'AT+CRFOP={self.tx_power}\r\n')
        threading.Event().wait(1)

        self.write_serial(f'AT+PARAMETER={self.lora_params}\r\n')
        threading.Event().wait(1)

        for _ in self.read_serial():
            pass  # Consume all responses

    def close(self):
        """
        Close the serial connection to the device.
        """
        if self.uart.is_open:
            self.uart.close()


class MessageHandler:
    """
    Handles message operations for the LoRa device.
    This class is responsible for sending and receiving messages,
    parsing received messages, and managing acknowledgments.

    Attributes:
        device_connection (DeviceConnection): The device connection object.
    """

    def __init__(self, device_connection):
        """
        Initialize the MessageHandler.

        Args:
            device_connection (DeviceConnection): The device connection object.
        """
        self.device_connection = device_connection

    def parse_received_message(self, received_data):
        """
        Parse the received message and extract relevant information.

        Args:
            received_data (str): The received data string.

        Returns:
            dict: A dictionary containing parsed message information.
        """
        if "+RCV" not in received_data:
            return None

        data_parts = received_data.split(",")
        stationid = data_parts[0].split("=")[1]
        msgcontent = data_parts[2]
        rssi = data_parts[3]
        snr = data_parts[4]

        if "RPT" in msgcontent:
            return None

        return {
            "stationid": stationid,
            "msgcontent": msgcontent,
            "rssi": rssi,
            "snr": snr
        }

    def send_message(self, message):
        """
        Send a message using the LoRa device.

        Args:
            message (str): The message to be sent.

        Returns:
            str: A string describing the sent message.
        """
        message_length = len(message)
        message_to_send = f"AT+SEND=0,{message_length},{message}\r\n"
        self.device_connection.write_serial(message_to_send)
        return f"Message sent: {message}"

    def send_ack(self, stationid):
        """
        Send an acknowledgment message.

        Args:
            stationid (str): The station ID to acknowledge.

        Returns:
            str: A string describing the sent acknowledgment.
        """
        ack_message = f"ACK {stationid}"
        return self.send_message(ack_message)


class LRmsMessengerUI:
    """
    Manages the user interface for the LRms Messenger application.
    This class handles the console-based UI, including display updates,
    user input, and interaction with the MessageHandler and DeviceConnection.

    Attributes:
        device_connection (DeviceConnection): The device connection object.
        message_handler (MessageHandler): The message handler object.
        output_buffer (collections.deque): Buffer for storing output messages.
        stop_event (threading.Event): Event for signaling threads to stop.
    """

    def __init__(self, device_connection, message_handler, max_lines=100):
        """
        Initialize the LRmsMessengerUI.

        Args:
            device_connection (DeviceConnection): The device connection object.
            message_handler (MessageHandler): The message handler object.
            max_lines (int): Maximum number of lines in the output buffer.
        """
        self.device_connection = device_connection
        self.message_handler = message_handler
        self.output_buffer = deque(maxlen=max_lines)
        self.stop_event = threading.Event()

    def add_message(self, message):
        """
        Add a message to the output buffer.

        Args:
            message (str): The message to add.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.output_buffer.append(f"[{timestamp}] {message}")

    def display_menu(self):
        """
        Display the main menu.
        """
        voltage = self.get_battery_voltage()
        print(f"\nLRms Messenger Menu: Battery: {voltage:.2f} volts")
        print("1. Press G to get messages")
        print("2. Press S to send a message")
        print("3. Press Q to quit")

    def get_battery_voltage(self):
        """
        Get the current battery voltage.

        Returns:
            float: The battery voltage.
        """
        # This is a placeholder function. Replace it with actual ADC reading if available.
        return 3.7  # Dummy value for battery voltage

    def handle_input(self):
        """
        Handle user input.

        Returns:
            bool: True if the application should continue, False to exit.
        """
        choice = input("Enter your choice: ").upper()

        if choice == 'G':
            self.get_messages()
        elif choice == 'S':
            self.send_message()
        elif choice == 'Q':
            print("Exiting program...")
            return False
        else:
            print("Invalid choice. Please try again.")

        return True

    def get_messages(self):
        """
        Retrieve and display messages from the LoRa device.
        """
        messages_received = False
        for received_data in self.device_connection.read_serial():
            messages_received = True
            parsed_message = self.message_handler.parse_received_message(
                received_data)
            if parsed_message:
                self.display_message(parsed_message)

        if not messages_received:
            print("There are no messages...")

    def display_message(self, message):
        """
        Display a parsed message.

        Args:
            message (dict): The parsed message dictionary.
        """
        print("-" * 45)
        print(f"Message from: {message['stationid']}")
        print(f"RSSI: {message['rssi']} SNR: {message['snr']}")
        print(message['msgcontent'])
        print("-" * 45)

    def send_message(self):
        """
        Send a message using the LoRa device.
        """
        message = input("Enter your message: ")
        result = self.message_handler.send_message(message)
        print(result)

    def run(self):
        """
        Run the main application loop.
        """
        while not self.stop_event.is_set():
            self.display_menu()
            if not self.handle_input():
                self.stop_event.set()
                break

        self.device_connection.close()


def main():
    """
    Main function to set up and run the application.
    """
    try:
        device_connection = DeviceConnection()
        device_connection.configure_device()
        message_handler = MessageHandler(device_connection)
        ui = LRmsMessengerUI(device_connection, message_handler)
        ui.run()
    except serial.SerialException as e:
        print(f"Serial Error: {e}")
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
