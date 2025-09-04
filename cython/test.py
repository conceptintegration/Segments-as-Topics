
import angular_distance as ad
import time
import random
import numpy as np


v = np.array([random.uniform(-5.0,5.0) for _ in range(10000)])
w = np.array([random.uniform(-5.0,5.0) for _ in range(10000)])

t1 = time.time()
distance = ad.angular_distance(v,w)
t2 = time.time()
t = t2-t1
print("%.10f" % t, "seconds")
print(distance)

