# Zhihao Zhang
# NGSIM dataset processor dataloader

import pandas as pd
import numpy as np
import os


class NGSIMTrajdata:
    def __init__(self, file_path: str):
        assert os.path.isfile(file_path)
        self.df = pd.read_csv(file_path, sep=" ", header=None, skipinitialspace=True)
        self.car2start = {}
        self.frame2cars = {}
        col_names = ['id', 'frame', 'n_frames_in_dataset', 'epoch', 'local_x',
                     'local_y', 'global_x', 'global_y', 'length', 'width', 'class',
                     'speed', 'acc', 'lane', 'carind_front', 'carind_rear',
                     'dist_headway', 'time_headway', 'global_heading']
        self.df.columns = col_names
        for (dfind, carid) in enumerate(self.df['id']):
            if carid not in self.car2start:
                self.car2start[carid] = dfind
            frame = int(self.df.loc[dfind, ['frame']])
            if frame not in self.frame2cars:
                self.frame2cars[frame] = [carid]
            else:
                self.frame2cars[frame].append(carid)
        print("Finish data set initialization!")
        self.nframes = max(self.frame2cars.keys())


def carsinframe(trajdata: NGSIMTrajdata, frame: int):
    return trajdata.frame2cars[frame]


def carid_set(trajdata: NGSIMTrajdata):
    return set(trajdata.car2start.keys())


def nth_carid(trajdata: NGSIMTrajdata, frame: int, n: int):
    return trajdata.frame2cars[frame][n-1]


def first_carid(trajdata: NGSIMTrajdata, frame: int):
    return nth_carid(trajdata, frame, 1)


def iscarinframe(trajdata: NGSIMTrajdata, carid: int, frame: int):
    return carid in carsinframe(trajdata, frame)

    # given frame and carid, find index of car in trajdata
    # Returns 0 if it does not exist


def car_df_index(trajdata: NGSIMTrajdata, carid: int, frame: int):
    df = trajdata.df
    lo = trajdata.car2start[carid]
    framestart = df.loc[lo, 'frame']

    retval = 0

    if framestart == frame:
        retval = lo
    elif frame >= framestart:
        retval = frame - framestart + lo
        n_frames = df.loc[lo, 'n_frames_in_dataset']
        if retval > lo + n_frames:
            retval = 0

    return retval


def get_frame_range(trajdata: NGSIMTrajdata, carid: int):
    lo = trajdata.car2start[carid]
    framestart = trajdata.df.loc[lo, 'frame']

    n_frames = trajdata.df.loc[lo, 'n_frames_in_dataset']
    frameend = framestart + n_frames  # in julia there us a -1 but since python's range doesn't include end index
    return range(framestart, frameend)


def pull_vehicle_headings(trajdata: NGSIMTrajdata, v_cutoff: float = 2.5, smoothing_width: float = 0.5):
    df = trajdata.df

    for carid in carid_set(trajdata):
        frames = [i for i in get_frame_range(trajdata, carid)]


dirname, filename = os.path.split(os.path.abspath(__file__))

NGSIM_TRAJDATA_PATHS = [
                        os.path.join(dirname, "../data/i101_trajectories-0750am-0805am.txt"),
                        os.path.join(dirname, "../data/i101_trajectories-0805am-0820am.txt"),
                        os.path.join(dirname, "../data/i101_trajectories-0820am-0835am.txt"),
                        os.path.join(dirname, "../data/i80_trajectories-0400-0415.txt"),
                        os.path.join(dirname, "../data/i80_trajectories-0500-0515.txt"),
                        os.path.join(dirname, "../data/i80_trajectories-0515-0530.txt"),
                       ]


def load_ngsim_trajdata(filepath: str):
    return NGSIMTrajdata(filepath)




