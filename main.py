import time

import numpy as np

from controllers.measure import Measurement
from controllers.oscilloscopeController import OscilloscopeController, OSC_COMMANDS

ARDUINO_PORT = '/dev/tty.usbmodem1401'
MOKU_IP = '192.168.73.1'

def main():
    oscilloscope_controller = None
    rotor_mount_controller = None
    moku_controller = None

    try:
        oscilloscope_controller = OscilloscopeController()
        oscilloscope_controller.connect()
        print('Oscilloscope connected')

        time_scale = oscilloscope_controller.send_query(OSC_COMMANDS['TimeScale'])
        time_scale = float(time_scale)
        print(f'Time scale: {time_scale}')

        laser_pulse_width = 200e-6
        laser_time_active = laser_pulse_width * 100
        laser_time_inactive = 1 - laser_time_active
        print(f'Laser time active: {laser_time_active}')


        # rotor_mount_controller = RotorMountController(port=ARDUINO_PORT)
        # rotor_mount_controller.connect()
        # print('Rotor mount controller connected')

        # moku_controller = MokuController(mokuIP=MOKU_IP)
        # moku_controller.connect()
        # print('Moku connected')

        # rotor_mount_controller.set_rotor_angle(90)
        # rotor_mount_controller.set_rotor_angle(120)
        # rotor_mount_controller.set_rotor_angle(13)
        # rotor_mount_controller.get_rotor_angle()

        # moku_controller.generate_waveform(channel=1, waveType='Pulse', amplitude=1.0, frequency=100, duty=0)
        # moku_controller.generate_waveform(channel=2, waveType='Square', amplitude=1.0, frequency=1e3, duty=0)

        measure = Measurement(oscilloscope_controller)
        measure.measure_single_event_picks(channel="CHAN1", outputfile_name="test2")

        for i in range(1):
            print(f'Iteration: {i}')
            measure.measure_count_events(channel="CHAN1", num_iters=1000, outputfile_name=f"measure_count-{i}")
            mean_events = count_events_per_second(f"measure_count-{i}.txt", time_scale, laser_time_active, laser_time_inactive)
            print(f'Mean events per second: {mean_events}')
            print("restarting")

    except Exception as e:
        print(f'Error: {e}')

    finally:
        if oscilloscope_controller:
            oscilloscope_controller.disconnect()
        if rotor_mount_controller:
            rotor_mount_controller.disconnect()
        if moku_controller:
            moku_controller.disconnect()


def count_events_per_second(file_name, time_scale, active_time, inactive_time, time_div=14):
    events = np.loadtxt(file_name)
    mean_events = np.mean(events)
    print(f'Mean events: {mean_events}')

    num_events_per_second = mean_events / (time_scale*time_div)
    num_events_active = mean_events * active_time
    num_events_inactive = 50 * inactive_time

    print(f'Events per second: {num_events_active + num_events_inactive}')

    return num_events_per_second


if __name__ == '__main__':
    main()
