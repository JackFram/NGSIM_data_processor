# Zhihao Zhang
# roadway class in python
from curves import CurvePt
from Vec import VecSE2
import math
import re


class LaneBoundary:
    def __init__(self, style: str, color: str):
        self.style = style
        self.color = color


class SpeedLimit:
    def __init__(self, lo: float, hi: float):
        self.lo = lo
        self.hi = hi

NULL_BOUNDARY = LaneBoundary("unknown", "unknown")
DEFAULT_SPEED_LIMIT = SpeedLimit(-math.inf, math.inf)
DEFAULT_LANE_WIDTH = 3.0

class LaneTag:
    def __init__(self, segment: int, lane: int):
        self.segment = segment
        self.lane = lane


class RoadIndex:
    def __init__(self, ind: CurvePt.CurveIndex, tag: LaneTag):
        self.ind = ind
        self.tag = tag


NULL_ROADINDEX = RoadIndex(CurvePt.CurveIndex(-1, None), LaneTag(-1,-1))


class LaneConnection:
    def __init__(self, downstream: bool, mylane: CurvePt.CurveIndex, target: RoadIndex):
        self.downstream = downstream
        self.mylane = mylane
        self.target = target


def parse_lane_connection(line: str):
    cleanedline = re.sub(r"(\(|\))", "", line)
    tokens = cleanedline.split()
    assert tokens[0] == "D" or tokens[0] == "U"
    downstream = (tokens[0] == "D")
    mylane = CurvePt.CurveIndex(int(tokens[1]), float(tokens[2]))
    target = RoadIndex(
                CurvePt.CurveIndex(int(tokens[3]), float(tokens[4])),
                LaneTag(int(tokens[5]), int(tokens[6]))
            )
    return LaneConnection(downstream, mylane, target)


class Lane:
    def __init__(self, tag: LaneTag, curve: list, width: float = DEFAULT_LANE_WIDTH, speed_limit: SpeedLimit = DEFAULT_SPEED_LIMIT,
                 boundary_left: LaneBoundary = NULL_BOUNDARY, boundary_right: LaneBoundary = NULL_BOUNDARY, exits: list = [], entrances: list = [],
                 next: RoadIndex = NULL_ROADINDEX, prev: RoadIndex = NULL_ROADINDEX):
        self.tag = tag
        self.curve = curve
        self.width = width
        self.speed_limit = speed_limit
        self.boundary_left = boundary_left
        self.boundary_right = boundary_right
        self.exits = exits
        self.entrances = entrances

        if next != NULL_ROADINDEX:
            self.exits.insert(0, LaneConnection(True, CurvePt.curveindex_end(self.curve), next))

        if prev != NULL_ROADINDEX:
            self.entrances.insert(0, LaneConnection(False, CurvePt.CURVEINDEX_START, prev))


class RoadSegment:
    def __init__(self, id: int, lanes: list):
        self.id = id
        self.lanes = lanes


class Roadway:
    def __init__(self, segments: list = []):
        self.segments = segments


def read_roadway(fp):
    lines = fp.readlines()
    line_index = 0
    if "ROADWAY" in lines[line_index]:
        line_index += 1

    nsegs = int(lines[line_index].strip())
    line_index += 1

    roadway = Roadway()
    for i_seg in range(nsegs):
        segid = int(lines[line_index].strip())
        line_index += 1
        nlanes = int(lines[line_index].strip())
        line_index += 1
        seg = RoadSegment(segid, [])
        for i_lane in range(nlanes):
            assert i_lane == int(lines[line_index].strip())
            line_index += 1
            tag = LaneTag(segid, i_lane)
            width = float(lines[line_index].strip())
            tokens = (lines[line_index].strip()).split()
            line_index += 1
            speed_limit = SpeedLimit(float(tokens[0]), float(tokens[1]))
            tokens = (lines[line_index].strip()).split()
            line_index += 1
            boundary_left = LaneBoundary(tokens[0], tokens[1])
            tokens = (lines[line_index].strip()).split()
            line_index += 1
            boundary_right = LaneBoundary(tokens[0], tokens[1])
            exits = []
            entrances = []
            n_conns = int(lines[line_index].strip())
            line_index += 1
            for i_conn in range(n_conns):
                conn = parse_lane_connection(lines[line_index].strip())
                line_index += 1
                if conn.downstream:
                    exits.append(conn)
                else:
                    entrances.append(conn)
            npts = int(lines[line_index].strip())
            line_index += 1
            curve = []
            for i_pt in range(npts):
                line = lines[line_index].strip()
                line_index += 1
                cleanedline = re.sub(r"(\(|\))", "", line)
                tokens = cleanedline.split()
                x = float(tokens[0])
                y = float(tokens[1])
                theta = float(tokens[2])
                s = float(tokens[3])
                k = float(tokens[4])
                kd = float(tokens[5])
                curve.append(CurvePt.CurvePt(VecSE2.VecSE2(x, y, theta), s, k, kd))
            seg.lanes.append(Lane(tag, curve, width=width, speed_limit=speed_limit,
                                     boundary_left=boundary_left,
                                     boundary_right=boundary_right,
                                     entrances=entrances, exits=exits))
        roadway.segments.append(seg)
    return roadway




