import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.pyplot import title
from matplotlib.ticker import ScalarFormatter
from scipy.signal import find_peaks

from controllers.oscilloscopeController import OscilloscopeController, OSC_COMMANDS


def plot_signal(t, signal, save_name, peaks=None, title='Signal', x_label='Time (s)', y_label='Amplitude'):
    """
    Plot a signal with peaks
    :param t: time
    :param signal: signal
    :param save_name: save name
    :param peaks: peaks in the signal
    :param title: plot title (default: 'Signal with Peaks')
    :param x_label: x label (default: 'Time (s)')
    :param y_label: y label (default: 'Amplitude')
    """
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['mathtext.fontset'] = 'cm'

    # If you want to use latex
    # plt.rcParams['text.usetex'] = True
    # plt.rcParams['font.family'] = 'serif'

    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
    ax.plot(t, signal, color='black', linewidth=1.5, label="Signal")
    if peaks is not None:
        ax.scatter(t[peaks], signal[peaks], color='red', s=100, label="Peaks", edgecolor='black', zorder=5)

    ax.set_title(title, fontsize=18)
    ax.set_xlabel(x_label, fontsize=14)
    ax.set_ylabel(y_label, fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)

    ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    ax.set_xlim([0, max(t)])
    ax.set_ylim([signal.min() - 0.5, signal.max() + 0.5])

    ax.grid(True, color='gray', linestyle='-', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    # plt.show()
    plt.savefig(save_name)


class Measurement:
    height = 2
    distance = 2

    def __init__(self, oscilloscope: OscilloscopeController, folder='data'):
        self.folder = folder
        self.oscilloscope = oscilloscope

    def count_events(self, channel: str):
        """
        Count the number of events in a signal
        :param channel: oscilloscope channel
        :return: number of events, frequency of the signal measured by the oscilloscope
        """
        signal, t, _ = self.oscilloscope.capture_waveform(channel)
        frequency = self.oscilloscope.send_query(OSC_COMMANDS['Frequency'])

        peaks, _ = find_peaks(signal, height=self.height, distance=self.distance)
        return peaks.size, float(frequency)

    def measure_count_events(self, channel, num_iters=1000, outputfile_name='temp_out.csv'):
        """
        Measure the number of events in a signal num_iters times
        :param channel: oscilloscope channel
        :param num_iters: number of iterations to measure
        :param outputfile_name: output file name
        """
        results = []
        totalConts = 0
        for i in range(num_iters):
            events, frequency = self.count_events(channel)
            results.append((events, frequency))
            totalConts += events

        mean_counts = totalConts / len(results)
        time_scale = self.oscilloscope.send_query(OSC_COMMANDS['TimeScale'])
        frequency = self.oscilloscope.send_query(OSC_COMMANDS['Frequency'])

        print("Mean counts:", mean_counts)
        print("Time scale (s):", float(time_scale))
        print("Time window (s):", float(time_scale) * 14.0)
        print("Counts over 1s:", mean_counts / (float(time_scale) * 14.0))
        print("Frecuecy:", frequency)

        df = pd.DataFrame(results, columns=['events', 'frequency'])
        data_name = self.validate_file_name(outputfile_name)
        df.to_csv(data_name, index=False)

    def measure_single_event(self, channel, count_peaks=True):
        """
        Measure the number of events in a signal num_iters times
        :param channel: oscilloscope channel
        :param count_peaks: count peaks in the signal
        """
        signal, t, _ = self.oscilloscope.capture_waveform(channel)
        frequency = self.oscilloscope.send_query(OSC_COMMANDS['Frequency'])
        peaks = None
        if count_peaks:
            peaks, _ = find_peaks(signal, height=self.height, distance=self.distance)

        data_name = self.validate_file_name('single_event_picks.csv')
        df_signal = pd.DataFrame({'time': t, 'signal': signal})
        df_signal.to_csv(data_name, index=False)

        image_name = self.validate_file_name('single_event_picks.png')
        title = ''
        if count_peaks:
            title = f'Frequency: {frequency} Hz - Number of Events: {peaks.size}'
        else:
            title = f'Frequency: {frequency} Hz'

        plot_signal(t, signal, image_name, peaks, title=title)

        print(f"Single event picks saved in {image_name} and {data_name}")

    def validate_file_name(self, file_name):
        """
        Validate if a file name already exists in the folder, if it does, add a number to the end of the file name
        :param file_name: file to validate
        :return: validated file name
        """
        folder_path = os.path.join(self.folder, file_name)
        file_exist = os.path.isfile(folder_path)

        file_name_without_ext = file_name.split('.')[0]
        file_name_ext = file_name.split('.')[1]
        i = 1

        while file_exist:
            new_file_name = f"{file_name_without_ext}_{i}.{file_name_ext}"
            folder_path = os.path.join(self.folder, new_file_name)
            file_exist = os.path.isfile(folder_path)
            i += 1

        return folder_path
