# Zhihao Zhang
# roadway class in python
from curves import CurvePt
from Vec import VecSE2, VecE2
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


NULL_LANETAG = LaneTag(0,0)


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

    def get_by_ind_roadway(self, ind: CurvePt.CurveIndex, roadway: Roadway):
        if ind.i == 0:
            pt_lo = prev_lane_point(self, roadway)
            pt_hi = self.curve[0]
            s_gap = norm(VecE2.VecE2(pt_hi.pos - pt_lo.pos))
            pt_lo = CurvePt.CurvePt(pt_lo.pos, -s_gap, pt_lo.k, pt_lo.kd)
            CurvePt.lerp(pt_lo, pt_hi, ind.t)
        elif ind.i < len(self.curve):
            return CurvePt.lerp(self.curve[ind.i - 1], self.curve[ind.i], ind.t)
        else:
            pt_hi = next_lane_point(self, roadway)
            pt_lo = self.curve[-1]
            s_gap = norm(VecE2.VecE2(pt_hi.pos - pt_lo.pos))
            pt_hi = CurvePt.CurvePt(pt_hi.pos, pt_lo.s + s_gap, pt_hi.k, pt_hi.kd)
            CurvePt.lerp(pt_lo, pt_hi, ind.t)


class RoadSegment:
    def __init__(self, id: int, lanes: list):
        self.id = id
        self.lanes = lanes


class Roadway:
    def __init__(self, segments: list = []):
        self.segments = segments

    def get_by_tag(self, tag: LaneTag):
        seg = self.get_by_id(tag.segment)
        return seg.lanes[tag.lane]

    def get_by_id(self, segid: int):
        for seg in self.segments:
            if seg.id == segid:
                return seg
        raise IndexError("Could not find segid {} in roadway".format(segid))

    def get_by_roadindex(self, roadindex: RoadIndex):
        lane = self.get_by_tag(roadindex.tag)
        return lane.get_by_ind_roadway(roadindex.ind, self)


def read_roadway(fp):
    lines = fp.readlines()
    fp.close()
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


class RoadProjection:
    def __init__(self, curveproj: CurvePt.CurveProjection, tag: LaneTag):
        self.curveproj = curveproj
        self.tag = tag


def next_lane(lane: Lane, roadway: Roadway):
    return roadway.get_by_tag(lane.exits[0].target.tag)


def prev_lane(lane: Lane, roadway: Roadway):
    return roadway.get_by_tag(lane.entrances[1].target.tag)


def next_lane_point(lane: Lane, roadway: Roadway):
    return roadway.get_by_roadindex(lane.exits[0].target)


def prev_lane_point(lane: Lane, roadway: Roadway):
    return roadway.get_by_roadindex(lane.entrances[0].target)


def proj_1(posG: VecSE2.VecSE2, lane: Lane, roadway: Roadway, move_along_curves: bool = True):
    curveproj = proj(posG, lane.curve)
    rettag = lane.tag
    if curveproj.ind == CurvePt.CurveIndex(1, 0.0) and has_prev(lane):
        pt_lo = prev_lane_point(lane, roadway)
        pt_hi = lane.curve[0]
        t = get_lerp_time_unclamped(pt_lo, pt_hi, posG)
        if t <= 0.0 and move_along_curves:
            return proj_1(posG, prev_lane(lane, roadway), roadway)
        elif t < 1.0:
            assert ((not move_along_curves) or 0.0 <= t < 1.0)
            # t was computed assuming a constant angle
            # this is not valid for the large distances and angle disparities between lanes
            # thus we now use a bisection search to find the appropriate location

            t, footpoint = get_closest_perpendicular_point_between_points(pt_lo.pos, pt_hi.pos, posG)

            ind = CurvePt.CurveIndex(0, t)
            curveproj = get_curve_projection(posG, footpoint, ind)
    elif curveproj.ind == curveindex_end(lane.curve) and has_next(lane):
        pt_lo = lane.curve[-1]
        pt_hi = next_lane_point(lane, roadway)
        t = get_lerp_time_unclamped(pt_lo, pt_hi, posG)
        if t >= 1.0 and move_along_curves:
            return proj_1(posG, next_lane(lane, roadway), roadway)
        elif t >= 0.0:
            assert ((not move_along_curves) or 0.0 <= t < 1.0)
            # t was computed assuming a constant angle
            # this is not valid for the large distances and angle disparities between lanes
            # thus we now use a bisection search to find the appropriate location

            t, footpoint = get_closest_perpendicular_point_between_points(pt_lo.pos, pt_hi.pos, posG)

            ind = CurvePt.CurveIndex(len(lane.curve), t)
            curveproj = get_curve_projection(posG, footpoint, ind)
    return RoadProjection(curveproj, rettag)


def proj_2(posG: VecSE2.VecSE2, roadway: Roadway):

    best_dist2 = math.inf
    best_proj = RoadProjection(CurvePt.CurveProjection(CurvePt.CurveIndex(-1, -1), None, None), NULL_LANETAG)

    for seg in roadway.segments:
        for lane in seg.lanes:
            roadproj = proj_1(posG, lane, roadway, move_along_curves=False)  # return RoadProjection
            targetlane = roadway.get_by_tag(roadproj.tag)  # return Lane
            footpoint = targetlane[roadproj.curveproj.ind, roadway]  # TODO: write a get method
            dist2 = VecE2.normsquared(VecE2.VecE2(posG - footpoint.pos))
            if dist2 < best_dist2:
                best_dist2 = dist2
                best_proj = roadproj

    return best_proj





