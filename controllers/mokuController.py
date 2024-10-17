from moku.instruments import WaveformGenerator

class MokuController:
    def __init__(self, mokuIP):
        self.mokuIP = mokuIP
        self.i = None

    def connect(self):
        try:
            self.i = WaveformGenerator(self.mokuIP, force_connect=True)
            print('Connected to Moku')

        except Exception as e:
            print(f'Error while connecting Moku: {e}')
            raise e

    def generate_waveform(self, channel, waveType, amplitude, frequency, duty=None):
        try:
            self.i.generate_waveform(channel=channel, type=waveType, amplitude=amplitude, frequency=frequency, duty=duty)
        except Exception as e:
            print(f'Exception occurred: {e}')

    def disconnect(self):
        try:
            if self.i:
                self.i.close()
        except Exception as e:
            print(f'Error while disconnecting Moku: {e}')
