import numpy as np
import os
import time
from datetime import datetime
import requests
import board
import json

# https://github.com/adafruit/Adafruit_CircuitPython_LSM6DS/blob/main/adafruit_lsm6ds/__init__.py
# https://github.com/adafruit/Adafruit_CircuitPython_LSM6DS/blob/main/adafruit_lsm6ds/ism330dhcx.py
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX
# from adafruit_lsm6ds.lsm6dsox import LSM6DSOX

from adafruit_lsm6ds import Rate, AccelRange, GyroRange
import busio
import digitalio

from fps_counter import FPSCounter
from parameters import DATASETS_FOLDER

import keyboard
import psutil


LED_EVENT_START_TIME = time.time()
START_BUTTON_PUSHED = False

# filter out repeat events
LAST_KEYPRESS_TIME = time.time()


# define the callback function
def on_keypress(e):
    global LAST_KEYPRESS_TIME
    global START_BUTTON_PUSHED

    # filter out repeat key presses less than half a second apart
    if time.time() - LAST_KEYPRESS_TIME > 0.5:
        LAST_KEYPRESS_TIME = time.time()

        if e.name == 'space':
            START_BUTTON_PUSHED = True


keyboard.on_press(on_keypress, suppress=True)


def realtime_loop(sensor, led_red, led_green, led_blue):
    '''
    actually runs the algorithm
    '''

    t0 = 0
    last_led_time = 0
    last_put_time = 0
    last_alert_time = 0

    mean_accel = np.zeros(3)
    mean_gyro = np.zeros(3)
    mean_tau = 0.999

    fps = FPSCounter(params={'display_every_k_seconds': 2})

    global START_BUTTON_PUSHED

    while not START_BUTTON_PUSHED:

        # get data
        timestamp = datetime.now().isoformat()
        accel = sensor.acceleration
        gyro = sensor.gyro

        for k in range(3):
            mean_accel[k] = mean_accel[k] * mean_tau + accel[k] * (1.0 - mean_tau)
            mean_gyro[k] = mean_gyro[k] * mean_tau + gyro[k] * (1.0 - mean_tau)

        # flash red when running real-time code
        if time.time() - last_led_time > 0.25:
            led_red.value = not led_red.value   # flash red at 2 Hz
            led_green.value = True
            led_blue.value = True

            last_led_time = time.time()

        if time.time() - last_put_time > 0.2:
            # for testing, put a new value to the webserver
            url = "http://192.168.4.1:8000/update"
            try:
                #requests.put(url + '/' + '<br><br>' + datetime.now().isoformat() + '<br>accel<br>' + str(accel[0]) + '<br>'+ str(accel[1]) + '<br>'+ str(accel[2])  + '<br>gyro<br>' + str(gyro[0]) + '<br>'+ str(gyro[1]) + '<br>'+ str(gyro[2]) , verify=False, timeout=1.0)

                if time.time() - last_alert_time > 10:
                    last_alert_time = time.time()
                    alert_now = 'Unusual Driving Detected!'
                else:
                    alert_now = 'Normal Driving'

                accel_scaled = [0, 0, 0]
                gyro_scaled = [0, 0, 0]

                for k in range(3):
                    accel_scaled[k] = max(min(1.0, accel[k] - mean_accel[k]), -1.0)
                    gyro_scaled[k] = max(min(1.0, gyro[k] - mean_gyro[k]), -1.0)

                requests.put(url + '/' + json.dumps({'bar1': accel_scaled[0], 'bar2': accel_scaled[1], 'bar3': accel_scaled[2],
                                                     'bar4': gyro_scaled[0], 'bar5': gyro_scaled[1], 'bar6': gyro_scaled[2],
                                                     'alert': alert_now}))

            except:
                print('cannot put..')
                pass

            last_put_time = time.time()

        # process data

        # check on memory usage

        if time.time() - t0 > 5:
            print()
            print('*********************************************')
            print(psutil.virtual_memory().percent)
            print(psutil.swap_memory().percent)
            print('*********************************************')
            print()

            t0 = time.time()

        fps.update()

    print()
    print('<<< Finished real-time code! >>>')
    print()

    START_BUTTON_PUSHED = False


def listener_loop():

    global START_BUTTON_PUSHED
    global LAST_KEYPRESS_TIME

    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = ISM330DHCX(i2c)

    sensor.accelerometer_range = AccelRange.RANGE_2G
    sensor.accelerometer_data_rate = Rate.RATE_833_HZ

    sensor.gyro_range = GyroRange.RANGE_125_DPS
    sensor.gyro_data_rate = Rate.RATE_833_HZ

    led_red = digitalio.DigitalInOut(board.D22)  # D22: pin 15
    led_red.direction = digitalio.Direction.OUTPUT

    led_green = digitalio.DigitalInOut(board.D17)  # D17: pin 11
    led_green.direction = digitalio.Direction.OUTPUT

    led_blue = digitalio.DigitalInOut(board.D27)  # D27: pin 13
    led_blue.direction = digitalio.Direction.OUTPUT

    led_red.value = True  # off
    led_green.value = True  # off
    led_blue.value = True  # off

    last_led_time = time.time()

    # flash green on boot, while waiting to start

    print()
    print('Starting listener loop. Press <space> to start/stop real-time code. Press any other key for keyboard test.')
    print()

    while True:
        # if any key pressed and not recording: blue for one second to verify keyboard works
        if time.time() - LAST_KEYPRESS_TIME < 0.5 and not START_BUTTON_PUSHED:
            # print()
            # print('Key pressed!')
            # print()
            #

            led_red.value = True
            led_green.value = True
            led_blue.value = False
            last_led_time = time.time()
        else:
            if time.time() - last_led_time > 1.0:
                led_red.value = not led_red.value
                led_green.value = True  # flash green at 2 Hz
                led_blue.value = True
                last_led_time = time.time()

        # if detect push of "start dataset" button, start recording
        if START_BUTTON_PUSHED:
            START_BUTTON_PUSHED = False

            print()
            print('>>> Starting real-time code! <<<')
            print()

            # this function will listen for push of button again to end the run:
            realtime_loop(sensor, led_red, led_green, led_blue)


if __name__ == '__main__':
    listener_loop()
