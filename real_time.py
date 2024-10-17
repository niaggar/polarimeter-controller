# %% Imports
from controllers.oscilloscopeController import OscilloscopeController, OSC_CHANNELS
from controllers.measure import Measurement, plot_signal

ARDUINO_PORT = '/dev/tty.usbmodem1401'
MOKU_IP = '192.168.73.1'


# %% Initialize oscilloscope
oscilloscope_controller = OscilloscopeController()
oscilloscope_controller.connect()

measure = Measurement(oscilloscope_controller, folder='./measures/constant') # Folder to save the measures

# %% Measure single event picks
measure.measure_single_event(channel=OSC_CHANNELS['CHANNEL_1'], count_peaks=True)   # Save a sample of the signal
measure.measure_single_event(channel=OSC_CHANNELS['CHANNEL_2'], count_peaks=False)  # Save the trigger signal

# %% Measure dark counts
measure.measure_count_events(channel=OSC_CHANNELS['CHANNEL_1'], outputfile_name='cuentas_oscuras.csv')

# %% Measure detector counts, save the results in a csv file
measure.measure_count_events(channel=OSC_CHANNELS['CHANNEL_1'], outputfile_name='laser-pulso-1.csv')

# %% Close oscilloscope
oscilloscope_controller.disconnect()

# %% Test
