# Zhihao Zhang
# NGSIM dataset processor trajdata.py file

import math


def symmetric_exponential_moving_average(arr: list, T: float, dt: float = 0.1):
    delta = T / dt
    N = len(arr)
    retval = []
    for i in range(N):
        Z = 0.0
        x = 0.0

        D = min(int(round(3 * delta)), i)

        if i + D > N - 1:
            D = N - i - 1

        for k in range(i - D, i + D + 1):
            e = math.exp(-abs(i-k)/delta)
            Z += e
            x += arr[k] * e

        retval.append(x / Z)

    return Z
