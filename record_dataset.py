
import time
from datetime import datetime

import board
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX
#from adafruit_lsm6ds.lsm6dsox import LSM6DSOX
from adafruit_lsm6ds import Rate, AccelRange, GyroRange
import busio
import digitalio

from fps_counter import FPSCounter

import keyboard


DATASET_TIMESTAMP = datetime.now().isoformat()
F_GROUND_TRUTH = open('/home/csaba/projects/datasets/' + DATASET_TIMESTAMP + '_ground_truth.txt', 'w')


LED_EVENT_START_TIME = time.time()


# catch keyboard events for ground truth:
def on_accelerate_event():
    # print()
    # print('ground truth: accelerate event!')
    # print()

    timestamp = datetime.now().isoformat()
    F_GROUND_TRUTH.write(timestamp + ' ' + 'accelerate' + '\n')

    global LED_EVENT_START_TIME
    LED_EVENT_START_TIME = time.time()

def on_turn_event():
    # print()
    # print('ground truth: turn event!')
    # print()

    timestamp = datetime.now().isoformat()
    F_GROUND_TRUTH.write(timestamp + ' ' + 'turn' + '\n')

    global LED_EVENT_START_TIME
    LED_EVENT_START_TIME = time.time()


def on_break_event():
    # print()
    # print('ground truth: break event!')
    # print()

    timestamp = datetime.now().isoformat()
    F_GROUND_TRUTH.write(timestamp + ' ' + 'break' + '\n')

    global LED_EVENT_START_TIME
    LED_EVENT_START_TIME = time.time()


def on_other_event():
    # print()
    # print('ground truth: other event!')
    # print()

    timestamp = datetime.now().isoformat()
    F_GROUND_TRUTH.write(timestamp + ' ' + 'other' + '\n')

    global LED_EVENT_START_TIME
    LED_EVENT_START_TIME = time.time()


# define the callback function
def on_keypress(e):
    if e.name == '1':
        on_accelerate_event()
    if e.name == '2':
        on_turn_event()
    if e.name == '3':
        on_break_event()
    if e.name == '4':
        on_other_event()


keyboard.on_press(on_keypress, suppress=False)

#
# keyboard.add_hotkey('1', on_accelerate_event)
# keyboard.add_hotkey('2', on_turn_event)
# keyboard.add_hotkey('3', on_break_event)
# keyboard.add_hotkey('4', on_other_event)


def record_dataset():

    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = ISM330DHCX(i2c)

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

    f = open('/home/csaba/projects/datasets/' + DATASET_TIMESTAMP + '_accelerometer.txt', 'w')

    print()
    print('starting recording...')
    print()

    last_led_time = time.time()
    global LED_EVENT_START_TIME

    #t0 = time.time()
    while True:  #time.time() < t0 + 10:
        #print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (sensor.acceleration))
        #print("Gyro X:%.2f, Y: %.2f, Z: %.2f radians/s" % (sensor.gyro))
        #print("")

        if time.time() - LED_EVENT_START_TIME < 0.5:
            led_blue.value = True
            led_red.value = False
        elif time.time() - last_led_time > 0.5:
            led_red.value = True
            led_blue.value = not led_blue.value  # flash blue at 2 Hz
            last_led_time = time.time()

        timestamp = datetime.now().isoformat()
        accel = sensor.acceleration
        # gyro = sensor.gyro
        f.write(timestamp + ',' + str(accel[0]) + ',' + str(accel[1]) + ',' + str(accel[2]) + '\n')

        fps.update()

        #event = keyboard.read_event()
        #if event is not None:
        #    on_keypress(event)

    # Not used for infinite recording:

    # print('finished recording.')
    # print()
    #
    # fps.update(force_display=True)
    # f.close()


if __name__ == '__main__':
    # use without a venv for now for adafruit stuff on raspberry pi
    record_dataset()
