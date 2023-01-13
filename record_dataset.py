
import time
from datetime import datetime

import board
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX
from adafruit_lsm6ds import Rate, AccelRange, GyroRange
import busio
import digitalio

from fps_counter import FPSCounter


def record_dataset():
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = LSM6DSOX(i2c)

    # old:
    #         self.redPin = 15
    #         self.greenPin = 11
    #         self.bluePin = 13

    led_red = digitalio.DigitalInOut(board.D22)  # D22: pin 15
    led_red.direction = digitalio.Direction.OUTPUT

    led_green = digitalio.DigitalInOut(board.D17)  # D17: pin 11
    led_green.direction = digitalio.Direction.OUTPUT

    led_blue = digitalio.DigitalInOut(board.D27)  # D27: pin 13
    led_blue.direction = digitalio.Direction.OUTPUT

    led_red.value = True  # off
    led_green.value = True  # off
    led_blue.value = True  # off

    sensor.accelerometer_range = AccelRange.RANGE_2G
    sensor.accelerometer_data_rate = Rate.RATE_833_HZ

    fps = FPSCounter(params={'display_every_k_seconds': 1})

    timestamp = datetime.now().isoformat()
    f = open('/home/csaba/datasets/' + timestamp + '_accelerometer.txt', 'w')

    print()
    print('starting recording...')
    print()

    last_led_time = time.time()

    #t0 = time.time()
    while True:  #time.time() < t0 + 10:
        #print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (sensor.acceleration))
        #print("Gyro X:%.2f, Y: %.2f, Z: %.2f radians/s" % (sensor.gyro))
        #print("")

        if time.time() - last_led_time > 0.5:
            led_blue.value = not led_blue.value  # flash blue at 2 Hz

        timestamp = datetime.now().isoformat()
        accel = sensor.acceleration
        # gyro = sensor.gyro
        f.write(timestamp + ',' + str(accel[0]) + ',' + str(accel[1]) + ',' + str(accel[2]) + '\n')

        fps.update()

    # Not used for infinite recording:

    # print('finished recording.')
    # print()
    #
    # fps.update(force_display=True)
    # f.close()


if __name__ == '__main__':
    # use without a venv for now for adafruit stuff on raspberry pi
    record_dataset()
