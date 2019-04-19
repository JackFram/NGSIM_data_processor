# Zhihao Zhang
# NGSIM dataset processor trajdata.py file

import math
import os
import numpy as np
from src import ngsim_trajdata
from src import trajectory_smoothing
from Vec import VecSE2
from src import const
from Roadway import roadway
from Record import record
from Basic import Vehicle
from tqdm import tqdm



NGSIM_TIMESTEP = const.NGSIM_TIMESTEP
SMOOTHING_WIDTH_POS = const.SMOOTHING_WIDTH_POS # [s]
METERS_PER_FOOT = const.METERS_PER_FOOT
DIR = const.DIR


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


def filter_trajectory(ftr: FilterTrajectoryResult, v: trajectory_smoothing.VehicleSystem = trajectory_smoothing.VehicleSystem()):

    mu = [ftr.x_arr[0], ftr.y_arr[0], ftr.theta_arr[0], ftr.v_arr[0]]
    sigma = 1e-1
    cov_ = np.diag([sigma * 0.01, sigma * 0.01, sigma * 0.1, sigma])

    # assume control is centered
    u = [0.0, 0.0]
    z = [None, None]

    for i in range(1, len(ftr)):

        # pull observation
        z[0] = ftr.x_arr[i]
        z[1] = ftr.y_arr[i]

        # apply extended Kalman filter
        mu, cov_ = trajectory_smoothing.EKF(v, mu, cov_, u, z)

        # strong result
        ftr.x_arr[i] = mu[0]
        ftr.y_arr[i] = mu[1]
        ftr.theta_arr.append(mu[2])
        ftr.v_arr.append(mu[3])

    return ftr


def copy(trajdata: ngsim_trajdata.NGSIMTrajdata, ftr: FilterTrajectoryResult):
    dfstart = trajdata.car2start[ftr.carid]
    N = trajdata.df.loc[dfstart, 'n_frames_in_dataset']

    # copy results back to trajdata

    for i in range(N):
        trajdata.df.loc[dfstart + i, 'global_x'] = ftr.x_arr[i]
        trajdata.df.loc[dfstart + i, 'global_y'] = ftr.y_arr[i]
        # trajdata.df[dfstart + i, 'speed'] = ftr.v_arr[i]
        if i > 0:
            trajdata.df[dfstart + i, 'speed'] = math.hypot(ftr.x_arr[i] - ftr.x_arr[i-1],
                                                           ftr.y_arr[i] - ftr.y_arr[i-1]) / NGSIM_TIMESTEP
        else:
            trajdata.df[dfstart + i, 'speed'] = math.hypot(ftr.x_arr[i + 1] - ftr.x_arr[i],
                                                           ftr.y_arr[i + 1] - ftr.y_arr[i]) / NGSIM_TIMESTEP
        trajdata.df[dfstart + i, 'global_heading'] = ftr.theta_arr[i]

    return trajdata


def filter_given_trajectory(trajdata: ngsim_trajdata.NGSIMTrajdata, carid: int):
    # Filters the given vehicle's trajectory using an Extended Kalman Filter

    ftr = FilterTrajectoryResult(trajdata, carid)

    # run pre-smoothing
    ftr.x_arr = symmetric_exponential_moving_average(ftr.x_arr, SMOOTHING_WIDTH_POS)
    ftr.y_arr = symmetric_exponential_moving_average(ftr.y_arr, SMOOTHING_WIDTH_POS)

    ftr = filter_trajectory(ftr)

    trajdata = copy(trajdata, ftr)

    return trajdata


def load_ngsim_trajdata(filepath: str, autofilter: bool = True):
    print("loading from file: ")
    tdraw = ngsim_trajdata.NGSIMTrajdata(filepath)

    if autofilter and os.path.splitext(filepath)[1] == ".txt":
        print("filtering:         ")
        for carid in tqdm(ngsim_trajdata.carid_set(tdraw)):
            tdraw = filter_given_trajectory(tdraw, carid)

    return tdraw


def convert(tdraw: ngsim_trajdata.NGSIMTrajdata, roadway: roadway.Roadway):
    df = tdraw.df
    vehdefs = {}
    states = []
    frames = []

    print("convert: Vehicle definition")

    for id, dfind in tqdm(tdraw.car2start):
        vehdefs[id] = Vehicle.VehicleDef(df.loc[dfind, 'class'],
                                        df.loc[dfind, 'length'] * METERS_PER_FOOT,
                                        df.loc[dfind, 'width'] * METERS_PER_FOOT)

    state_ind = -1
    print("convert: frames and states")
    for frame in tqdm(range(1, tdraw.nframes + 1)):

        frame_lo = state_ind + 1

        for id in ngsim_trajdata.carsinframe(tdraw, frame):
            dfind = ngsim_trajdata.car_df_index(tdraw, id, frame)
            assert dfind != -1

            posG = VecSE2.VecSE2(df.loc[dfind, 'global_x'] * METERS_PER_FOOT,
                                 df.loc[dfind, 'global_y'] * METERS_PER_FOOT,
                                 df.loc[dfind, 'global_heading'])
            speed = df.loc[dfind, 'speed'] * METERS_PER_FOOT
            state_ind += 1
            states[state_ind] = record.RecordState(Vehicle.VehicleState(posG, roadway, speed), id)

        frame_hi = state_ind
        frames[frame] = record.RecordFrame(frame_lo, frame_hi)

    return record.ListRecord(NGSIM_TIMESTEP, frames, states, vehdefs)


def get_corresponding_roadway(filename: str):
    if "i101" in filename:
        return const.ROADWAY_101
    else:
        return const.ROADWAY_80


def convert_raw_ngsim_to_trajdatas():
    for filepath in const.NGSIM_TRAJDATA_PATHS:
        filename = os.path.split(filepath)[1]
        print("converting " + filename)

        roadway = get_corresponding_roadway(filename)
        print("finish loading roadway.")
        print("Start loading NGSIM trajectory data.")
        tdraw = load_ngsim_trajdata(filepath)
        print("finish loading NGSIM trajectory data.")
        print("Start converting.")
        # no problems until here
        trajdata = convert(tdraw, roadway)
        outpath = os.path.join(DIR, "../data/trajdata_" + filename)
        fp = open(outpath, "w")
        trajdata.write(fp)
        fp.close()


# def load_trajdata(filepath: str):
#     td = open(io->read(io, MIME"text/plain"(), Trajdata), filepath, "r")
#     return td







