'''
A more sophisticated and pythonic version of the LRms-beaconmaster.py script.
Aiming for a modular design and easier to add to down the road.
'''

from datetime import datetime
import curses
from collections import deque
import threading
import serial

BEACON_INTERVAL = 60  # seconds

class DeviceConnection:
    """
    Manages the connection and communication with the LoRa device.

    This class handles the serial connection, device configuration, and
    basic read/write operations for RYLR993 or RYLR998 LoRa modules.

    Attributes:
        ser (serial.Serial): Serial connection object.
        device_type (str): Type of the LoRa device ('RYLR993' or 'RYLR998').
        rf_freq (int): Radio frequency in Hz.
        node_id (int): Node ID for the device.
        tx_power (int): Transmission power in dBm.
        lora_params (str): LoRa parameters string.
    """

    def __init__(self, port='/dev/ttyS0', rf_freq=867500000, node_id=1, tx_power=22, lora_params='9,7,1,12', device_type='RYLR993'):
        """
        Initialise the DeviceConnection.

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
        self.ser = serial.Serial(port, baud_rates[device_type], timeout=1)
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
            data = self.ser.readline().decode('utf-8').strip()
            if not data:
                break
            yield data

    def write_serial(self, text):
        """
        Write data to the serial connection.

        Args:
            text (str): Text to be written to the serial connection.
        """
        self.ser.write(text.encode())

    def configure_device(self):
        """
        Configure the LoRa device with the specified settings.

        This method sends a series of AT commands to set up the device
        according to the initialised parameters.
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
        if self.ser.is_open:
            self.ser.close()

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

class BeaconMasterUI:
    """
    Manages the user interface for the Beacon Master application.

    This class handles the curses-based UI, including display updates,
    user input, and interaction with the Commander and DeviceConnection.

    Attributes:
        stdscr (curses.window): The main curses window.
        device_connection (DeviceConnection): The device connection object.
        commander (Commander): The commander object for sending commands.
        max_lines (int): Maximum number of lines in the output buffer.
        output_buffer (collections.deque): Buffer for storing output messages.
        input_active (bool): Flag indicating if input is active.
        user_input (str): Current user input string.
        beacon_text (str): Text to be used for beaconing.
        stop_event (threading.Event): Event for signaling threads to stop.
    """

    def __init__(self, stdscr, device_connection, commander, max_lines=100):
        """
        Initialise the BeaconMasterUI.

        Args:
            stdscr (curses.window): The main curses window.
            device_connection (DeviceConnection): The device connection object.
            commander (Commander): The commander object for sending commands.
            max_lines (int): Maximum number of lines in the output buffer.
        """
        self.stdscr = stdscr
        self.device_connection = device_connection
        self.commander = commander
        self.max_lines = max_lines
        self.output_buffer = deque(maxlen=max_lines)
        self.input_active = False
        self.user_input = ""
        self.beacon_text = "LRms Beacon"
        self.setup_curses()
        self.stop_event = threading.Event()

    def setup_curses(self):
        """
        Set up the curses environment.
        """
        curses.curs_set(0)
        self.stdscr.clear()
        self.stdscr.refresh()
        self.height, self.width = self.stdscr.getmaxyx()

    def display_banner(self):
        """
        Display the banner at the top of the screen.
        """
        banner = " Welcome to LRms Beacon Master V2.0 by Andy Kirby "
        self.stdscr.addstr(0, 0, banner.center(self.width), curses.A_REVERSE)
        self.stdscr.addstr(1, 0, "-" * (self.width - 1))

    def display_output(self):
        """
        Display the output buffer on the screen.
        """
        for idx, line in enumerate(self.output_buffer):
            if idx + 2 < self.height - 2:
                self.stdscr.addstr(idx + 2, 0, line[:self.width-1])

    def display_input_field(self):
        """
        Display the input field at the bottom of the screen.
        """
        if self.input_active:
            prompt = "Enter Beacon Text (Max 50 chars): "
            self.stdscr.addstr(self.height - 1, 0, prompt + self.user_input)
        else:
            self.stdscr.addstr(self.height - 1, 0, " " * (self.width - 1))

    def add_message(self, message):
        """
        Add a message to the output buffer.

        Args:
            message (str): The message to add.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.output_buffer.append(f"[{timestamp}] {message}")

    def handle_input(self, ch):
        """
        Handle user input.

        Args:
            ch (int): The character input by the user.

        Returns:
            bool: True if the application should continue, False to exit.
        """
        if ch == ord('q'):
            return False
        elif ch == ord('b'):
            self.input_active = not self.input_active
        elif self.input_active:
            if ch == 10:  # Enter key
                self.beacon_text = self.user_input
                self.add_message(f"New beacon text set: {self.beacon_text}")
                self.user_input = ""
                self.input_active = False
            elif ch == 27:  # Escape key
                self.input_active = False
                self.user_input = ""
            elif ch == curses.KEY_BACKSPACE or ch == 127:
                self.user_input = self.user_input[:-1]
            elif len(self.user_input) < 50:
                self.user_input += chr(ch)
        return True

    def update(self):
        """
        Update the screen display.
        """
        self.stdscr.clear()
        self.display_banner()
        self.display_output()
        self.display_input_field()
        self.stdscr.refresh()

    def run(self):
        """
        Run the main application loop.
        """
        beacon_thread = threading.Thread(target=self.send_beacon)
        beacon_thread.start()

        serial_read_thread = threading.Thread(target=self.read_serial)
        serial_read_thread.start()

        while not self.stop_event.is_set():
            self.update()
            ch = self.stdscr.getch()
            if not self.handle_input(ch):
                self.stop_event.set()
                break

        beacon_thread.join()
        serial_read_thread.join()
        self.device_connection.close()

    def send_beacon(self):
        """
        Send beacon messages at regular intervals.
        """
        while not self.stop_event.is_set():
            message = self.commander.send_at_command(self.beacon_text)
            self.add_message(f"Beaconing: {message}")
            self.stop_event.wait(BEACON_INTERVAL)

    def read_serial(self):
        """
        Continuously read from the serial port.
        """
        while not self.stop_event.is_set():
            for data in self.device_connection.read_serial():
                self.add_message(f"Received: {data}")
            self.stop_event.wait(0.1)

def main(stdscr):
    """
    Main function to set up and run the application.

    Args:
        stdscr (curses.window): The main curses window.
    """
    try:
        device_connection = DeviceConnection()
        device_connection.configure_device()
        commander = Commander(device_connection)
        ui = BeaconMasterUI(stdscr, device_connection, commander)
        ui.run()
    except serial.SerialException as e:
        stdscr.addstr(0, 0, f"Serial Error: {e}")
        stdscr.refresh()
        stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)
