from pyfirmata import Arduino, util
import time

import matplotlib.pyplot  as plt

if __name__ == '__main__':
    board = Arduino('/dev/ttyACM0')
    print("Communication Successfully Initiated ")
    it = util.Iterator(board)
    it.start()
    
    analog_0 = board.get_pin('a:0:i')
    analog_0.enable_reporting()
    start_Time = time.time()
    count = 0
    time_recording = []
    force = []
    while count < 100000:
        count = count + 1
        current_time = time.time()
        frequency = count/(current_time-start_Time)
        voltage = analog_0.read()
        print('frequency:', frequency, ' voltage:', voltage)
        time_recording.append(current_time - start_Time)
        force.append(voltage)
        time.sleep(0.0001)
plt.plot(time_recording, force)
plt.show()

