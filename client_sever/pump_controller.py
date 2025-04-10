import serial
import time
import sys

class SerialControl:
    """
    A simpler class to control a device over serial,
    waiting for acknowledgments using the serial timeout.
    """

    def __init__(self, port, baudrate=9600, timeout=5.0):
        """
        Initializes the serial connection.

        Args:
            port (str): The serial port name (e.g., 'COM3', '/dev/ttyUSB0').
            baudrate (int): The communication speed. Defaults to 9600.
            timeout (float): Max time in seconds for readline() to wait for data.
                             This acts as the ACK timeout. Defaults to 5.0 seconds.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout # Single timeout for read operations
        self.ser = None

        try:
            # The timeout here is crucial for ACK waiting
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2) # Allow connection to settle
            if self.ser.is_open:
                print(f"Successfully connected to {self.port} at {self.baudrate} baud (Timeout: {self.timeout}s).")
                self.ser.reset_input_buffer() # Clear any old data
            else:
                print(f"Failed to open port {self.port}.")
                self.ser = None
        except serial.SerialException as e:
            print(f"Error opening serial port {self.port}: {e}")
            self.ser = None
        except Exception as e:
            print(f"An unexpected error during initialization: {e}")
            self.ser = None

    def send_command(self, cmd, expected_ack=None):
        """
        Sends a command and optionally waits for a specific acknowledgment.

        Args:
            cmd (str): The command string to send.
            expected_ack (str | None): The exact acknowledgment string expected.
                                       If None, just sends command and reads one line.

        Returns:
            str | None:
                - The received acknowledgment string if expected_ack was provided and matched.
                - The received line if expected_ack was None and a line was read.
                - None if the command failed, timed out waiting for ACK,
                  or the received ACK did not match the expected one.
        """
        if not self.ser or not self.ser.is_open:
            print("Error: Serial port is not open.")
            return None

        try:
            # Prepare and send command
            command_bytes = (cmd + '\r\n').encode('utf-8') # Adjust '\r\n' if needed
            print(f"Sending: {cmd!r}")
            self.ser.reset_input_buffer() # Clear buffer before send/read
            self.ser.write(command_bytes)
            self.ser.flush()

            # Read response - readline() will wait up to self.timeout seconds
            print(f"Waiting for response (max {self.timeout}s)...")
            response_bytes = self.ser.readline()
            response_str = response_bytes.decode('utf-8', errors='ignore').strip()

            if response_str:
                print(f"Received: {response_str!r}")
                if expected_ack is not None:
                    if response_str == expected_ack:
                        print("ACK Matched.")
                        return response_str # Success! ACK received.
                    else:
                        print(f"ACK Mismatch. Expected '{expected_ack}', got '{response_str}'.")
                        return None # Failure - Wrong ACK received.
                else:
                    # No specific ACK expected, return what we got
                    return response_str # Success - Got some response line.
            else:
                # readline() timed out (returned empty bytes)
                print("Timeout: No response received.")
                return None # Failure - Timeout

        except serial.SerialException as e:
            print(f"Serial error during send/receive: {e}")
            return None # Failure - Serial error
        except Exception as e:
            print(f"An unexpected error occurred during send/receive: {e}")
            return None # Failure - Other error

    def open_pump(self):
        """
        Sends the 'OPEN' command and waits for its specific acknowledgment.
        *** Modify command and expected ACK as needed! ***
        """
        open_cmd = "OPEN_DEVICE_CMD"            # Replace with your actual command
        expected_response = "OK: pump is on" # Replace with your actual ACK

        print("\nAttempting to send OPEN command...")
        response = self.send_command(open_cmd, expected_ack=expected_response)

        if response is not None:
            print("--> OPEN command successful.")
        else:
            print("--> OPEN command failed (Timeout or wrong ACK).")
        return response # Returns ACK string on success, None on failure

    def close_pump(self):
        """
        Sends the 'CLOSE' command and waits for its specific acknowledgment.
        *** Modify command and expected ACK as needed! ***
        """
        close_cmd = "CLOSE_DEVICE_CMD"           # Replace with your actual command
        expected_response = "OK: pump is off" # Replace with your actual ACK

        print("\nAttempting to send CLOSE command...")
        response = self.send_command(close_cmd, expected_ack=expected_response)

        if response is not None:
            print("--> CLOSE command successful.")
        else:
            print("--> CLOSE command failed (Timeout or wrong ACK).")
        return response # Returns ACK string on success, None on failure

    def close_connection(self):
        """ Closes the serial connection. """
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                print(f"Serial port {self.port} closed.")
            except Exception as e:
                 print(f"Error closing serial port {self.port}: {e}")
        self.ser = None

    def __enter__(self):
        """ Enter context manager """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Exit context manager - ensures connection close """
        self.close_connection()

# --- Example Usage ---
if __name__ == "__main__":
    # --- CONFIGURATION ---
    SERIAL_PORT = 'COM4' # Replace with your port
    BAUD_RATE = 9600
    # Single timeout for reading acknowledgments (in seconds)
    ACK_TIMEOUT = 5.0
    # --------------------

    print(f"Attempting to connect to {SERIAL_PORT}...")

    # Use 'with' statement for automatic connection closing
    try:
        with SerialControl(SERIAL_PORT, BAUD_RATE, timeout=ACK_TIMEOUT) as controller:
            if not controller.ser:
                print("Could not establish serial connection. Exiting.")
                sys.exit(1)

            # --- Test OPEN command ---
            ack = controller.open_pump()
            if ack: # Check if ack is not None
                # Proceed if open was successful
                print(f"Device reported: {ack}")
                time.sleep(2) # Wait a bit

                # --- Test CLOSE command ---
                ack_close = controller.close_pump()
                if ack_close:
                    print(f"Device reported: {ack_close}")
                else:
                    print("Close command did not receive expected ACK.")

                time.sleep(1)

            else:
                print("Open command failed, cannot proceed.")


        print("\nExited 'with' block, connection automatically closed.")

    except Exception as e:
         # Catch potential errors during __init__ or outside command calls
         print(f"\nAn error occurred: {e}")

    print("\nScript finished.")