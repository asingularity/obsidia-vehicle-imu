import datetime
import pickle
import time
import os
import pprint
import numpy as np
import subprocess
from scipy.io import loadmat, savemat


def save_array_to_mat(mat_filename, arr, arr_name):
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.savemat.html
    savemat(file_name=mat_filename, mdict={arr_name: arr})

def save_dict_to_mat(mat_filename, dict_to_save):
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.savemat.html
    savemat(file_name=mat_filename, mdict=dict_to_save)


def get_all_mat_arrays_in_folder(folder_path):
    mats_dict = {}

    filenames = os.listdir(folder_path)
    for filename in filenames:
        if '.mat' in filename.lower():
            mats_dict[filename] = get_array_from_mat(mat_filename=os.path.join(folder_path, filename))

    return mats_dict


def get_array_from_mat(mat_filename):
    '''

    get array from mat file; will fail if more than one array
    assumes there is one array in the file

    :param mat_filename:
    :return:
    '''

    mat_dict = loadmat(mat_filename)
    return get_array_from_mat_dict(mat_dict=mat_dict)


def get_array_from_mat_dict(mat_dict):
    arr_key = None
    arr_key_count = 0

    for key in mat_dict.keys():
        if type(mat_dict[key]) is np.ndarray:
            arr_key = key
            arr_key_count += 1

    assert arr_key_count < 2, '!!! Error !!! Found more than one array in mat file: ' #+ mat_filename
    assert arr_key_count > 0, '!!! Error !!! Found no array in mat file: ' #+ mat_filename

    return mat_dict[arr_key]
