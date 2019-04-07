# Zhihao Zhang
# NGSIM dataset processor trajdata.py file

import math
from src import ngsim_trajdata


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

    return retval


class FilterTrajectoryResult:
    def __init__(self, trajdata: ngsim_trajdata.NGSIMTrajdata, carid: int):
        dfstart = trajdata.car2start[carid]
        N = trajdata.df.loc[dfstart, 'n_frames_in_dataset']
        x_arr = []
        y_arr = []
        theta_arr = []
        v_arr = []
        for i in range(N):
            x_arr.append(trajdata.df.loc[dfstart + i, 'global_x'])
            y_arr.append(trajdata.df.loc[dfstart + i, 'global_y'])
        theta_arr.append(math.atan2(y_arr[4] - y_arr[0], x_arr[4] - x_arr[0]))
        v_arr.append(trajdata.df.loc[dfstart, 'speed'])
        # hypot(ftr.y_arr[lookahead] - y₀, ftr.x_arr[lookahead] - x₀)/ν.Δt
        if v_arr[0] < 1.0:  # small speed
            # estimate with greater lookahead
            theta_arr[0] = math.atan2(y_arr[-1] - y_arr[0], x_arr[-1] - x_arr[0])
        self.carid = carid
        self.x_arr = x_arr
        self.y_arr = y_arr
        self.theta_arr = theta_arr
        self.v_arr = v_arr

    def __len__(self):
        return len(self.x_arr)




