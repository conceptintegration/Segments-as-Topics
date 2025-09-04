from libc.math cimport sqrt
from libc.math cimport acos
import numpy as np
cimport numpy as np

cdef cosine_cy(np.ndarray[np.float64_t] v, np.ndarray[np.float64_t] w):
    vv: np.float64_t=0.0
    ww: np.float64_t=0.0
    vw: np.float64_t=0.0
    i: np.int64_t
    for i in range(len(v)):
        vv+=v[i]*v[i]
        ww+=w[i]*w[i]
        vw+=v[i]*w[i]
    return 1.0-vw/sqrt(vv*ww)

cpdef angular_distance(np.ndarray[np.float64_t] v, np.ndarray[np.float64_t] w):
    """
    Compute inverse of angular distance between to vectors v and w
    """
    return 1 - (acos(1 - cosine_cy(v,w))/np.pi)
