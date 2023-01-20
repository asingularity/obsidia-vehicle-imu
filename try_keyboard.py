import keyboard
import time
from datetime import datetime

DATASET_TIMESTAMP = datetime.now().isoformat()
F_GROUND_TRUTH = open('test_ground_truth.txt', 'w')
F_GROUND_TRUTH.close()

LED_EVENT_START_TIME = time.time()



# catch keyboard events for ground truth:
def on_accelerate_event():
    # print()
    # print('ground truth: accelerate event!')
    # print()
    #print('1 pressed!!!')
    timestamp = datetime.now().isoformat()

    f_ground_truth = open('test_ground_truth.txt', 'a')
    f_ground_truth.write(timestamp + ' ' + 'accelerate' + '\n')
    f_ground_truth.close()

    global LED_EVENT_START_TIME
    LED_EVENT_START_TIME = time.time()


def on_turn_event():
    # print()
    # print('ground truth: turn event!')
    # print()
    print('2 pressed!!!')
    timestamp = datetime.now().isoformat()
    F_GROUND_TRUTH.write(timestamp + ' ' + 'turn' + '\n')

    global LED_EVENT_START_TIME
    LED_EVENT_START_TIME = time.time()


def on_break_event():
    # print()
    # print('ground truth: break event!')
    # print()
    print('3 pressed!!!')
    timestamp = datetime.now().isoformat()
    F_GROUND_TRUTH.write(timestamp + ' ' + 'break' + '\n')

    global LED_EVENT_START_TIME
    LED_EVENT_START_TIME = time.time()


def on_other_event():
    # print()
    # print('ground truth: other event!')
    # print()
    print('4 pressed!!!')
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


keyboard.on_press(on_keypress, suppress=True)

from fps_counter import FPSCounter

if __name__ == '__main__':
    fps = FPSCounter()

    while True:
        fps.update()
        on_accelerate_event()
