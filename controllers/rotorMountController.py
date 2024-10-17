import serial
import time

class RotorMountController:
    def __init__(self, port, baudrate=57600, timeout=1):
        self.ser = None
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

    def connect(self):
        """
        Connect to the Arduino Rotor Mount Controller
        :return:
        """
        try:
            self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
            time.sleep(1)
            if self.ser.is_open:
                print(f'Connected to {self.port}')
            else:
                print(f'Failed to connect to {self.port}')
            
        except Exception as e:
            print(f'Error while connecting Rotor Mount Controller: {e}')
            raise e

    def disconnect(self):
        """
        Disconnect from the Arduino Rotor Mount Controller
        :return:
        """
        try:
            if self.ser:
                self.ser.close()
        except Exception as e:
            print(f'Error while disconnecting Rotor Mount Controller: {e}')

    def send_command(self, command):
        """
        Send a command to the Arduino Rotor Mount Controller
        :param command: command to send
        :return: response from the Arduino Rotor Mount Controller
        """
        command += '\r\n'
        self.ser.write(command.encode())
        time.sleep(0.1)
        return self.ser.readline().decode('utf-8').strip()

    def set_rotor_angle(self, angle: float):
        """
        Set the rotor angle
        :param angle: value in degrees
        :return:
        """
        command = f'SRA {angle}'
        response = self.send_command(command)
        print(f'Set rotor angle to {angle} degrees: {response}')

    def get_rotor_angle(self):
        """
        Get the current rotor angle
        :return: current rotor angle in degrees
        """
        response = self.send_command('GRA')
        print(f'Current rotor angle: {response} degrees')
        return float(response)
