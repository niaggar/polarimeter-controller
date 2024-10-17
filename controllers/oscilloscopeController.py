import pyvisa
import sys
import time
import numpy as np

OSC_CHANNELS = {
    'CHANNEL_1': 'CHAN1',
    'CHANNEL_2': 'CHAN2',
    'CHANNEL_3': 'CHAN3',
}

OSC_COMMANDS = {
    'Frequency': ':MEASure:FREQuency?', # :MEASure:FREQuency?
    'TimeScale': ':TIM:SCAL?',
}

class OscilloscopeController:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.scope = None

    def send_command(self, command: str):
        """
        Send a command to the oscilloscope
        :param command: command to send
        """
        self.scope.write(command)
        time.sleep(0.1)

    def send_query(self, command: str) -> str:
        """
        Send a query to the oscilloscope
        :param command: command to send
        :return: response from the oscilloscope
        """
        res = self.scope.query(command)
        return res

    def connect(self):
        """
        Connect to the oscilloscope
        """
        instruments = self.rm.list_resources()
        usb = list(filter(lambda x: 'USB' in x, instruments))
        if len(usb) != 1:
            print('Bad instrument list', instruments)
            sys.exit(-1)

        usb_name = usb[0]
        self.scope = self.rm.open_resource(usb_name, timeout=1000)
        reference = self.send_query('*IDN?')
        print(f'Connected to: {reference}')

    def disconnect(self):
        """
        Disconnect from the oscilloscope
        """
        try:
            if self.scope:
                self.scope.close()
            self.rm.close()

            print('Oscilloscope disconected')
        except Exception as e:
            print(f'Error while disconnecting Oscilloscope: {e}')

    def capture_waveform(self, channel):
        """
        Capture waveform from the oscilloscope
        :param channel: channel to capture
        :return:
            signal: captured signal.
            t: time vector.
            preamble: preamble of the captured signal.
        """
        scope = self.scope
        pre = scope.query(':WAV:PRE?').split(',')
        samp_freq = scope.query(':ACQ:SRAT?').split(',')

        preamble = {
            'format': int(pre[0]),
            'type': int(pre[1]),
            'points': int(pre[2]),
            'count': int(pre[3]),
            'Fs': float(samp_freq[0]),
            'x_increment': float(pre[4]),
            'x_origin': float(pre[5]),
            'x_reference': float(pre[6]),
            'y_increment': float(pre[7]),
            'y_origin': float(pre[8]),
            'y_reference': float(pre[9]),
        }

        scope.write(f':WAV:SOUR {channel}')
        scope.write(':WAV:MODE NORM')
        scope.write('WAV:DATA?')
        rawdata = scope.read_raw()

        data = np.frombuffer(rawdata[11:-1], 'B')
        signal = (data - preamble['y_origin'] - preamble['y_reference']) * preamble['y_increment']
        t = np.arange(0, (len(data)) * preamble['x_increment'], preamble['x_increment'])

        return signal, t, preamble
