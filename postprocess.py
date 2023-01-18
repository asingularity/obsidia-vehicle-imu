
import time
import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['agg.path.chunksize'] = 10000
import matplotlib.pyplot as plt

from matlab_utils import save_array_to_mat, get_array_from_mat

REF_TIMESTAMP = '2023-01-01T00:00:00.000000'


def _timestamp_str_to_float(timestamp_str):
    # Convert the timestamp string to a datetime object
    dt = datetime.datetime.fromisoformat(timestamp_str)

    # Use the timestamp function to convert the datetime object to a timestamp float
    timestamp = datetime.datetime.timestamp(dt)

    base = datetime.datetime.fromisoformat(REF_TIMESTAMP)
    base_timestamp = datetime.datetime.timestamp(base)

    return timestamp - base_timestamp


def _load_acc_file(filename):

    '''

    2023-01-13T11:57:11.781587,19.599609916600002,-19.599609916600002,-19.599609916600002
    2023-01-13T11:57:11.783448,0.5156532703,-1.2239287599,-9.56351372655
    2023-01-13T11:57:11.784870,0.52223353245,-1.24606236895,-9.55633525875
    2023-01-13T11:57:11.786250,0.526420972,-1.22213414295,-9.5270231819
    2023-01-13T11:57:11.787748,0.53539405675,-1.2143574695,-9.559326287

    END LINE MAY BE CUT OFF!!! IGNORE LAST NONEMPTY LINE!

    '''

    f = open(filename, 'r')

    lines = []

    for line in f:
        lines.append(line)

    timestamp_arr = []
    acc_x_arr = []
    acc_y_arr = []
    acc_z_arr = []
    acc_abs_arr = []

    num_lines = len(lines)
    for k in range(num_lines - 1):  # ignore last line
        line = lines[k]
        things = line.strip().split(',')
        #print(things)  # ['2023-01-13T11:57:11.781587', '19.599609916600002', '-19.599609916600002', '-19.599609916600002']

        timestamp_arr.append(_timestamp_str_to_float(things[0]))
        acc_x = float(things[1])
        acc_y = float(things[2])
        acc_z = float(things[3])

        acc_abs = np.sqrt(acc_x * acc_x + acc_y * acc_y + acc_z * acc_z)

        acc_x_arr.append(acc_x)
        acc_y_arr.append(acc_y)
        acc_z_arr.append(acc_z)
        acc_abs_arr.append(acc_abs)

    timestamp_arr = np.array(timestamp_arr)
    acc_x_arr = np.array(acc_x_arr)
    acc_y_arr = np.array(acc_y_arr)
    acc_z_arr = np.array(acc_z_arr)
    acc_abs_arr = np.array(acc_abs_arr)

    f.close()

    return timestamp_arr, acc_x_arr, acc_y_arr, acc_z_arr, acc_abs_arr


def _load_ground_truth_file(filename):

    f = open(filename, 'r')

    timestamp_arr = []
    events_arr = []

    for line in f:
        things = line.strip().split(' ')
        timestamp_arr.append(_timestamp_str_to_float(things[0]))
        if things[1].startswith('accel'):
            events_arr.append(1)
        elif things[1].startswith('turn'):
            events_arr.append(2)
        elif things[1].startswith('break'):
            events_arr.append(3)
        elif things[1].startswith('other'):
            events_arr.append(4)

    timestamp_arr = np.array(timestamp_arr)
    events_arr = np.array(events_arr)

    return timestamp_arr, events_arr


def postprocess_new_data(dataset_timestamp):

    num_subplots = 5
    fig_bar, ax = plt.subplots(nrows=num_subplots, ncols=1, sharex=True, figsize=(40, 20))

    timestamp_arr_acc, acc_x_arr, acc_y_arr, acc_z_arr, acc_abs_arr = _load_acc_file(filename=dataset_timestamp + '_accelerometer.txt')
    timestamp_arr_gt, events_arr = _load_ground_truth_file(filename=dataset_timestamp + '_ground_truth.txt')

    if dataset_timestamp.startswith('2023-01-13T14:28:30.932444'):
        for k in range(len(timestamp_arr_acc)):
            # 19233 1088937.5876090527
            # 19234 1179017.7017669678
            if timestamp_arr_acc[k] < 1179017:
                timestamp_arr_acc[k] = timestamp_arr_acc[k] + (1179017.7017669678 - 1088937.5876090527)
            #print(k, timestamp_arr_acc[k])

    #print(timestamp_arr_acc)
    #print()
    #print(timestamp_arr_gt)
    #print()

    save_array_to_mat(dataset_timestamp + '_accelerometer.mat', np.hstack((timestamp_arr_acc[:, np.newaxis], acc_x_arr[:, np.newaxis], acc_y_arr[:, np.newaxis], acc_z_arr[:, np.newaxis])), 'accelerometer')
    save_array_to_mat(dataset_timestamp + '_ground_truth_events.mat', np.hstack((timestamp_arr_gt[:, np.newaxis], events_arr[:, np.newaxis])), 'ground_truth_events')

    ax[0].cla()
    ax[0].plot(timestamp_arr_acc, acc_x_arr, 'r.')
    ax[0].get_xaxis().get_major_formatter().set_scientific(False)
    ax[0].get_yaxis().get_major_formatter().set_scientific(False)
    ax[0].set_title('accelerometer X')

    ax[1].cla()
    ax[1].plot(timestamp_arr_acc, acc_y_arr, 'g.')
    ax[1].get_xaxis().get_major_formatter().set_scientific(False)
    ax[1].get_yaxis().get_major_formatter().set_scientific(False)
    ax[1].set_title('accelerometer Y')

    ax[2].cla()
    ax[2].plot(timestamp_arr_acc, acc_z_arr, 'b.')
    ax[2].get_xaxis().get_major_formatter().set_scientific(False)
    ax[2].get_yaxis().get_major_formatter().set_scientific(False)
    ax[2].set_title('accelerometer Z')

    ax[3].cla()
    ax[3].plot(timestamp_arr_acc, acc_abs_arr, 'k.')
    ax[3].get_xaxis().get_major_formatter().set_scientific(False)
    ax[3].get_yaxis().get_major_formatter().set_scientific(False)
    ax[3].set_title('accelerometer ABS')

    ax[4].cla()
    ax[4].plot(timestamp_arr_gt, events_arr, 'ko')
    ax[4].get_xaxis().get_major_formatter().set_scientific(False)
    ax[4].get_yaxis().get_major_formatter().set_scientific(False)
    ax[4].set_title('ground truth events: 1:accelerate, 2:turn, 3:break, 4:bump')

    for k in range(len(events_arr)):
        event_t = timestamp_arr_gt[k]
        ax[0].axvline(x=event_t, color='g')
        ax[1].axvline(x=event_t, color='g')
        ax[2].axvline(x=event_t, color='g')
        ax[3].axvline(x=event_t, color='g')

    fig_bar.savefig("all_data.png", dpi=100)


def postporcess_with_results(dataset_timestamp):

    timestamp_arr_acc, acc_x_arr, acc_y_arr, acc_z_arr, acc_abs_arr = _load_acc_file(filename=dataset_timestamp + '_accelerometer.txt')
    timestamp_arr_gt, events_arr = _load_ground_truth_file(filename=dataset_timestamp + '_ground_truth.txt')

    results_start_time = 250

    results_tu = get_array_from_mat(mat_filename=dataset_timestamp + '_RESULT_tu.mat').flatten()
    results_fdet = get_array_from_mat(mat_filename=dataset_timestamp + '_RESULT_fdet.mat').flatten()

    print()
    print(results_tu.shape)
    #print(results_tu)
    print()

    print()
    print(results_fdet.shape)
    #print(results_fdet)
    print()

    num_subplots = 4
    fig_bar, ax = plt.subplots(nrows=num_subplots, ncols=1, sharex=True, figsize=(40, 20))

    ax[0].cla()
    ax[0].plot(timestamp_arr_acc, acc_x_arr, 'r.')
    ax[0].get_xaxis().get_major_formatter().set_scientific(False)
    ax[0].get_yaxis().get_major_formatter().set_scientific(False)
    ax[0].set_title('accelerometer X')

    ax[1].cla()
    ax[1].plot(timestamp_arr_acc, acc_y_arr, 'g.')
    ax[1].get_xaxis().get_major_formatter().set_scientific(False)
    ax[1].get_yaxis().get_major_formatter().set_scientific(False)
    ax[1].set_title('accelerometer Y')

    ax[2].cla()
    ax[2].plot(timestamp_arr_acc, acc_z_arr, 'b.')
    ax[2].get_xaxis().get_major_formatter().set_scientific(False)
    ax[2].get_yaxis().get_major_formatter().set_scientific(False)
    ax[2].set_title('accelerometer Z')

    # ax[3].cla()
    # ax[3].plot(timestamp_arr_acc, acc_abs_arr, 'k.')
    # ax[3].get_xaxis().get_major_formatter().set_scientific(False)
    # ax[3].get_yaxis().get_major_formatter().set_scientific(False)
    # ax[3].set_title('accelerometer ABS')

    # ax[4].cla()
    # ax[4].plot(timestamp_arr_gt, events_arr, 'ko')
    # ax[4].get_xaxis().get_major_formatter().set_scientific(False)
    # ax[4].get_yaxis().get_major_formatter().set_scientific(False)
    # ax[4].set_title('ground truth events: 1:accelerate, 2:turn, 3:break, 4:bump')

    ax[3].cla()
    ax[3].plot(timestamp_arr_acc[0] + results_start_time + results_tu, results_fdet, 'k-')
    ax[3].get_xaxis().get_major_formatter().set_scientific(False)
    ax[3].get_yaxis().get_major_formatter().set_scientific(False)
    ax[3].set_title('anomaly detection')

    for k in range(len(events_arr)):
        event_t = timestamp_arr_gt[k]
        event_type = events_arr[k]

        ax[0].axvline(x=event_t, color='g')
        ax[1].axvline(x=event_t, color='g')
        ax[2].axvline(x=event_t, color='g')
        #ax[3].axvline(x=event_t, color='g')

    fig_bar.savefig(dataset_timestamp + "_results.png", dpi=100)


def main():
    dataset_timestamp = '2023-01-13T11:57:10.525044'  # first car dataset
    # dataset_timestamp = '2023-01-13T14:28:30.932444'  # living room, test dataset; confusing
    # dataset_timestamp = '2023-01-14T17:03:46.266499'  # seated, should be more clear. X, Y, Z separate mostly

    #postprocess_new_data(dataset_timestamp)
    postporcess_with_results(dataset_timestamp)


if __name__ == '__main__':
    main()
