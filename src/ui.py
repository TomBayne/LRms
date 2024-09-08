"""
Handles the user interface for the Beacon Master application.
"""

import curses
from collections import deque
import threading
from datetime import datetime

BEACON_INTERVAL = 60

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
