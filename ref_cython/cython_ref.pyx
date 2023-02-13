
from libcpp cimport bool

import numpy as np
cimport numpy as np
cimport openmp

#DTYPE = np.int
#ctypedef np.int DTYPE_t

from cython.parallel import prange
cimport cython
from libc.math cimport tanh


# https://stackoverflow.com/questions/21851985/difference-between-np-int-np-int-int-and-np-int-t-in-cython


@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
@cython.cdivision(True)  # for modulo being fast
def run_matched_filters_cython(np.ndarray[np.float64_t, ndim=2] accel_buffer,
                               np.int32_t buffer_len,
                               np.int32_t new_data_index,
                               np.ndarray[np.float64_t, ndim=1] mfiltd1,
                               np.ndarray[np.float64_t, ndim=1] mfiltd2,
                               np.ndarray[np.float64_t, ndim=1] mfiltd3,
                               np.ndarray[np.float64_t, ndim=1] mfiltd4,
                               np.int32_t lm1,
                               np.int32_t lm2,
                               np.int32_t lm3,
                               np.int32_t lm4):

        #REAL-TIME UPDATE

        cdef np.int32_t ii, k, det_1, det_2, det_3, det_4

        det_1 = 0
        det_2 = 0
        det_3 = 0
        det_4 = 0

        cdef np.float64_t THdet1, THdet2, THdet3, THdet4, fs
        cdef np.float64_t ymfilt1_ii, ymfilt2_ii, ymfilt3_ii, ymfilt4_ii
        cdef np.float64_t ymfilt1_prev, ymfilt2_prev, ymfilt3_prev, ymfilt4_prev

        ymfilt1_prev = 0
        ymfilt2_prev = 0
        ymfilt3_prev = 0
        ymfilt4_prev = 0

        THdet1=7.9853      #detection threshold for matched filter1
        THdet2=3.3         #detection threshold for matched filter2
        THdet3=3.1         #detection threshold for matched filter3
        THdet4=4.0         #detection threshold for matched filter4
        fs=410.3614         #sampling rate that best matches to the actual samples

        for ii in range(new_data_index, buffer_len):

            ymfilt1_prev = ymfilt1_ii
            ymfilt2_prev = ymfilt2_ii
            ymfilt3_prev = ymfilt3_ii
            ymfilt4_prev = ymfilt4_ii

            ymfilt1_ii = 0
            ymfilt2_ii = 0
            ymfilt3_ii = 0
            ymfilt4_ii = 0

            for k in range(lm1):
                ymfilt1_ii = ymfilt1_ii + mfiltd1[k] * accel_buffer[ii-lm1+k, 0]
            ymfilt1_ii = 1/lm1 * ymfilt1_ii

            for k in range(lm2):
                ymfilt2_ii = ymfilt2_ii + mfiltd2[k] * accel_buffer[ii-lm2+k, 0]
            ymfilt2_ii = 1/lm2 * ymfilt2_ii

            for k in range(lm3):
                ymfilt3_ii = ymfilt3_ii + mfiltd3[k] * accel_buffer[ii-lm3+k, 1]
            ymfilt3_ii = 1/lm3 * ymfilt3_ii

            for k in range(lm4):
                ymfilt4_ii = ymfilt4_ii + mfiltd4[k] * accel_buffer[ii-lm4+k, 1]
            ymfilt4_ii = 1/lm4 * ymfilt4_ii

            #REAL-TIME DETECTION
            if ymfilt1_ii >THdet1 and ymfilt1_prev <= THdet1:
                det_1 = 1

            if ymfilt2_ii >THdet2 and ymfilt2_prev <= THdet2:
                det_2 = 1

            if ymfilt3_ii >THdet3 and ymfilt3_prev <= THdet3:
                det_3 = 1

            if ymfilt4_ii >THdet4 and ymfilt4_prev <= THdet4:
                det_4 = 1

    return det_1, det_2, det_3, det_4




























