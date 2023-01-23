import os
import time
from datetime import datetime

import board

# https://github.com/adafruit/Adafruit_CircuitPython_LSM6DS/blob/main/adafruit_lsm6ds/__init__.py
# https://github.com/adafruit/Adafruit_CircuitPython_LSM6DS/blob/main/adafruit_lsm6ds/ism330dhcx.py
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX
#from adafruit_lsm6ds.lsm6dsox import LSM6DSOX

from adafruit_lsm6ds import Rate, AccelRange, GyroRange
import busio
import digitalio

from fps_counter import FPSCounter
from parameters import DATASETS_FOLDER

import keyboard


SESSION_TIMESTAMP = datetime.now().isoformat()
GROUND_TRUTH_FILE_NAME = os.path.join(DATASETS_FOLDER, SESSION_TIMESTAMP + '_ground_truth.txt')
F_GROUND_TRUTH = open(GROUND_TRUTH_FILE_NAME, 'w')
F_GROUND_TRUTH.close()

LED_EVENT_START_TIME = time.time()

START_BUTTON_PUSHED = False

GROUND_TRUTH_EVENT_NOW = False

# filter out repeat events
LAST_KEYPRESS_TIME = time.time()


# catch keyboard events for ground truth:
def on_accelerate_event():
    # print()
    # print('ground truth: accelerate event!')
    # print()
    global GROUND_TRUTH_EVENT_NOW
    if not GROUND_TRUTH_EVENT_NOW:
        timestamp = datetime.now().isoformat()
        f_g = open(GROUND_TRUTH_FILE_NAME, 'a')
        f_g.write(timestamp + ' ' + 'start accelerate' + '\n')
        f_g.close()

        global LED_EVENT_START_TIME
        LED_EVENT_START_TIME = time.time()

        GROUND_TRUTH_EVENT_NOW = True


def on_turn_event():
    # print()
    # print('ground truth: turn event!')
    # print()
    global GROUND_TRUTH_EVENT_NOW
    if not GROUND_TRUTH_EVENT_NOW:

        timestamp = datetime.now().isoformat()
        f_g = open(GROUND_TRUTH_FILE_NAME, 'a')
        f_g.write(timestamp + ' ' + 'start turn' + '\n')
        f_g.close()

        global LED_EVENT_START_TIME
        LED_EVENT_START_TIME = time.time()

        GROUND_TRUTH_EVENT_NOW = True


def on_break_event():
    # print()
    # print('ground truth: break event!')
    # print()

    global GROUND_TRUTH_EVENT_NOW
    if not GROUND_TRUTH_EVENT_NOW:

        timestamp = datetime.now().isoformat()
        f_g = open(GROUND_TRUTH_FILE_NAME, 'a')
        f_g.write(timestamp + ' ' + 'start break' + '\n')
        f_g.close()

        global LED_EVENT_START_TIME
        LED_EVENT_START_TIME = time.time()

        GROUND_TRUTH_EVENT_NOW = True


def on_other_event():
    # print()
    # print('ground truth: other event!')
    # print()

    global GROUND_TRUTH_EVENT_NOW
    if not GROUND_TRUTH_EVENT_NOW:

        timestamp = datetime.now().isoformat()
        f_g = open(GROUND_TRUTH_FILE_NAME, 'a')
        f_g.write(timestamp + ' ' + 'start other' + '\n')
        f_g.close()

        global LED_EVENT_START_TIME
        LED_EVENT_START_TIME = time.time()

        GROUND_TRUTH_EVENT_NOW = True


def on_stop_event():
    global GROUND_TRUTH_EVENT_NOW
    if GROUND_TRUTH_EVENT_NOW:

        timestamp = datetime.now().isoformat()
        f_g = open(GROUND_TRUTH_FILE_NAME, 'a')
        f_g.write(timestamp + ' ' + 'end' + '\n')
        f_g.close()

        GROUND_TRUTH_EVENT_NOW = False


# define the callback function
def on_keypress(e):
    global LAST_KEYPRESS_TIME
    global START_BUTTON_PUSHED

    # filter out repeat key presses less than half a second apart
    if time.time() - LAST_KEYPRESS_TIME > 0.5:
        LAST_KEYPRESS_TIME = time.time()

        if e.name == '1':
            on_accelerate_event()
        if e.name == '2':
            on_turn_event()
        if e.name == '3':
            on_break_event()
        if e.name == '4':
            on_other_event()
        if e.name == 'esc':
            on_stop_event()
        if e.name == 'space':
            START_BUTTON_PUSHED = True


keyboard.on_press(on_keypress, suppress=True)


def record_dataset(sensor, led_red, led_green, led_blue, dataset_id):

    fps = FPSCounter(params={'display_every_k_seconds': 1})

    f_a = open(os.path.join(DATASETS_FOLDER, SESSION_TIMESTAMP + '_' + str(dataset_id) + '_accelerometer.txt'), 'w')
    f_g = open(os.path.join(DATASETS_FOLDER, SESSION_TIMESTAMP + '_' + str(dataset_id) + '_gyro.txt'), 'w')

    print()
    print('starting recording...')
    print()

    last_led_time = time.time()
    global LED_EVENT_START_TIME

    global START_BUTTON_PUSHED

    while not START_BUTTON_PUSHED:

        #print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (sensor.acceleration))
        #print("Gyro X:%.2f, Y: %.2f, Z: %.2f radians/s" % (sensor.gyro))
        #print("")

        if GROUND_TRUTH_EVENT_NOW:
            if time.time() - last_led_time > 0.25:
                led_red.value = not led_red.value  # flash red at 2 Hz
                led_green.value = True
                led_blue.value = True
                last_led_time = time.time()
        else:
            if time.time() - last_led_time > 0.25:
                led_red.value = True
                led_green.value = True
                led_blue.value = not led_blue.value  # flash blue at 2 Hz
                last_led_time = time.time()

        timestamp = datetime.now().isoformat()
        accel = sensor.acceleration
        gyro = sensor.gyro

        f_a.write(timestamp + ',' + str(accel[0]) + ',' + str(accel[1]) + ',' + str(accel[2]) + '\n')
        f_g.write(timestamp + ',' + str(gyro[0]) + ',' + str(gyro[1]) + ',' + str(gyro[2]) + '\n')

        fps.update()

    # Not used for infinite recording:

    print('finished recording.')
    print()
    #
    fps.update(force_display=True)
    f_a.close()
    f_g.close()

    START_BUTTON_PUSHED = False


def dataset_recorder_loop():

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
    dataset_id = 0

    while True:
        # if any key pressed and not recording: green for two seconds to verify keyboard works
        if time.time() - LAST_KEYPRESS_TIME < 2.0:
            led_red.value = True
            led_green.value = False
            led_blue.value = True
            last_led_time = time.time()
        else:
            if time.time() - last_led_time > 1.0:
                led_red.value = True
                led_green.value = True
                led_blue.value = not led_blue.value  # flash blue at 2 Hz
                last_led_time = time.time()

        # if detect push of "start dataset" button, start recording
        if START_BUTTON_PUSHED:

            START_BUTTON_PUSHED = False

            # this function will listen for push of button again to end the recording:
            record_dataset(sensor, led_red, led_green, led_blue, dataset_id)
            dataset_id += 1


if __name__ == '__main__':

    dataset_recorder_loop()

    # use without a venv for now for adafruit stuff on raspberry pi
