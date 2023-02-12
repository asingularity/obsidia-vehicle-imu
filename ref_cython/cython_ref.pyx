
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
                               np.ndarray[np.float64_t, ndim=1] mfiltd4):


    
    return




























