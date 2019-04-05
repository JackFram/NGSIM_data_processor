# Zhihao Zhang
# NGSIM dataset processor roadway class

import re
from Vec.VecE2 import *

FLOATING_POINT_REGEX = r'[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?'
METERS_PER_FOOT = 0.3048


class NGSIMRoadway:
    def __init__(self, name: str, boundaries: list, centerlines: list):
        self.name = name
        self.boundaries = boundaries
        self.centerlines = centerlines


class RoadwayInputParams:
    def __init__(self, filepath_boundaries: str, filepath_centerlines: str):
        self.filepath_boundaries = filepath_boundaries
        self.filepath_centerlines = filepath_centerlines


def read_boundaries(filepath_boundaries: str):
    fp = open(filepath_boundaries, 'r')
    lines = fp.readlines()
    for i, line in enumerate(lines):
        lines[i] = line.strip()
    assert lines[0] == 'BOUNDARIES'

    n_boundaries = int(lines[1])

    assert n_boundaries >= 0

    retval = []  # Array{Vector{VecE2}}

    line_index = 1
    for i in range(n_boundaries):
        line_index += 1
        assert lines[line_index] == "BOUNDARY {}".format(i+1)
        line_index += 1
        npts = int(lines[line_index])
        line = []  # Array{VecE2}
        for j in range(npts):
            line_index += 1
            matches = re.findall(FLOATING_POINT_REGEX, lines[line_index])
            x = float(matches[0]) * METERS_PER_FOOT
            y = float(matches[1]) * METERS_PER_FOOT
            line.append(VecE2(x, y))
        retval.append(line)
    return retval



