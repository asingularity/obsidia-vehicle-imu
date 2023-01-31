import os
from datetime import datetime
from parameters import DATASETS_FOLDER, RESULTS_FOLDER
from postprocess import _load_acc_file, _load_ground_truth_file, _timestamp_str_to_float
import numpy as np
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['agg.path.chunksize'] = 10000
import matplotlib.pyplot as plt


REF_TIMESTAMP = '2023-01-01T00:00:00.000000'

ACC_THRESH = 4.4


def _detect_accel_events(acc_arr, timestamp_arr):
    '''

    An event will be logged if the acceleration exceeds the threshold for at least 100ms.
    If the event lasts uninterrupted (stays above the threshold - 17% hysteresis) for more than 100ms, a single event is logged.
    A second event is logged if the acceleration drops below the threshold - 17% hysteresis for 100ms and then exceeds the threshold again for 100ms.

    Defaults: acceleration and braking 4.4m/s^2. Cornering 5.5m/s^2. These are set high to log a minimum number of events on most vehicles.
    Testing: artificially low to generate events. Acceleration and braking 3.0m/s^2. Cornering 3.5m/s^2
    In practice: choose levels between the defaults and the testing levels.

    :param acc_arr:
    :param timestamp_arr:
    :return:
    '''

    # types:
    #   1 for acceleration
    #   0 for end

    event_ongoing = False
    event_start_t = 0

    last_event_stop_t = -np.inf

    new_event_allowed = True

    detected_event_timestamps = []
    detected_event_types = []

    for k in range(len(acc_arr)):
        t = timestamp_arr[k]
        acc = acc_arr[k]

        if event_ongoing:
            if acc < ACC_THRESH - 0.17 * ACC_THRESH:
                if t - event_start_t > 0.1:
                    detected_event_timestamps.append(event_start_t)
                    detected_event_types.append(1)

                    detected_event_timestamps.append(t)
                    detected_event_types.append(0)

                    last_event_stop_t = t
                    new_event_allowed = False
                else:
                    pass

                event_ongoing = False

        elif not new_event_allowed:
            if acc > ACC_THRESH - 0.17 * ACC_THRESH:
                last_event_stop_t = t
            if t - last_event_stop_t > 0.1:
                new_event_allowed = True
        else:
            if acc > ACC_THRESH and new_event_allowed:

                event_ongoing = True
                event_start_t = t

    detected_event_timestamps = np.array(detected_event_timestamps)
    detected_event_types = np.array(detected_event_types)

    return detected_event_timestamps, detected_event_types


def process_dataset(session_timestamp, dataset_event_types, dataset_name, exp_path):

    dataset_index_str = '0'

    # load data

    timestamp_arr_acc, acc_x_arr, acc_y_arr, acc_z_arr, acc_abs_arr = _load_acc_file(filename=os.path.join(DATASETS_FOLDER, session_timestamp + '_' + dataset_index_str + '_accelerometer.txt'))
    timestamp_arr_gyro, gyro_x_arr, gyro_y_arr, gyro_z_arr, gyro_abs_arr = _load_acc_file(filename=os.path.join(DATASETS_FOLDER, session_timestamp + '_' + dataset_index_str + '_gyro.txt'))

    timestamp_arr_gt, events_arr = _load_ground_truth_file(filename=os.path.join(DATASETS_FOLDER, session_timestamp + '_ground_truth.txt'), event_types=dataset_event_types)

    num_subplots = 3
    fig_bar, ax = plt.subplots(nrows=num_subplots, ncols=1, sharex=True, figsize=(40, 20))

    ax[0].cla()
    ax[0].plot(timestamp_arr_acc, acc_x_arr, 'r.')
    ax[0].get_xaxis().get_major_formatter().set_scientific(False)
    ax[0].get_yaxis().get_major_formatter().set_scientific(False)
    ax[0].axhline(y=ACC_THRESH, color='b')
    ax[0].set_title(dataset_name + ' ' + 'accelerometer X, with detected events')

    ax[1].cla()
    ax[1].plot(timestamp_arr_acc, acc_x_arr, 'r.')
    ax[1].get_xaxis().get_major_formatter().set_scientific(False)
    ax[1].get_yaxis().get_major_formatter().set_scientific(False)
    # ax[1].axhline(y=ACC_THRESH, color='b')
    ax[1].set_title(dataset_name + ' ' + 'accelerometer X, with ground truth events')

    ax[2].cla()
    try:
        ax[2].plot(timestamp_arr_gt, events_arr, 'ko')
    except:
        print()
        print('timestamp_arr_gt', timestamp_arr_gt)
        print('events_arr', events_arr)
        print()
        raise

    ax[2].get_xaxis().get_major_formatter().set_scientific(False)
    ax[2].get_yaxis().get_major_formatter().set_scientific(False)
    ax[2].set_title(dataset_name + ' ' + 'ground truth events start: ' + str(dataset_event_types))

    for k in range(len(events_arr)):
        event_t = timestamp_arr_gt[k]
        ax[1].axvline(x=event_t, color='g')

    # detect events
    detected_event_timestamps, detected_event_types = _detect_accel_events(acc_arr=acc_x_arr, timestamp_arr=timestamp_arr_acc)

    for k in range(len(detected_event_timestamps)):
        event_t = detected_event_timestamps[k]
        ax[0].axvline(x=event_t, color='g')

    fig_bar.savefig(os.path.join(exp_path + "/" + dataset_name + "_accelerometer_data.png"), dpi=100)


def main():
    '''
    :return:
    '''
    pass

    experiment_timestamp = datetime.now().isoformat()
    print()
    experiment_name = input('experiment_name >> ')
    print()
    # make an experiment folder in RESULTS_FOLDER

    exp_name = 'thresh_method_' + experiment_timestamp + '_' + experiment_name
    print()
    print('exp_name:', exp_name)
    print()

    exp_path = os.path.join(RESULTS_FOLDER, exp_name)
    os.makedirs(exp_path)

    # load datasets

    datasets = {  # name, timestamp, event_types
        'mira_mesa_1': ('2023-01-21T13:06:39.069536', None),
        'mira_mesa_2': ('2023-01-21T14:17:09.160292', None),
        'park_driving_1': ('2023-01-22T14:17:09.241501', {'start accelerate': 1, 'start break': 2, 'start turn': 3, 'start other': 4, 'end': 0}),
        'park_driving_2': ('2023-01-23T11:11:45.184903', {'start accelerate': 1, 'start break': 2, 'start turn': 3, 'start other': 4, 'end': 0}),
        'OB_driving': ('2023-01-23T12:06:39.227689', {'start accelerate': 1, 'start break': 2, 'start turn': 3, 'end': 0}),
        'acceleration_training': ('2023-01-30T11:30:00.426262', {'start accel': 1, 'start break': 2, 'start turn_left': 3, 'start turn_right': 4, 'end': 0}),
        'braking_training': ('2023-01-30T11:30:00.703324', {'start accel': 1, 'start break': 2, 'start turn_left': 3, 'start turn_right': 4, 'end': 0}),
        'swerve_training': ('2023-01-30T11:30:00.475365', {'start accel': 1, 'start break': 2, 'start turn_left': 3, 'start turn_right': 4, 'end': 0}),
    }

    # run detector and display vs. ground truth events
    # calculate false positive rate

    for dataset_name in datasets.keys():
        (dataset_timestamp, dataset_event_types) = datasets[dataset_name]

        print()
        print('processing: ', dataset_name, ':', dataset_timestamp)
        print()

        process_dataset(session_timestamp=dataset_timestamp,
                        dataset_event_types=dataset_event_types,
                        dataset_name=dataset_name,
                        exp_path=exp_path)


if __name__ == '__main__':
    main()

