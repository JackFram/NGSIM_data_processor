from NGSIM_data_processor.Vec import VecSE2


class CurvePt:
    def __init__(self, pos: VecSE2.VecSE2, s: float, k=None, kd=None):
        self.pos = pos
        self.s = s
        self.k = k
        self.kd = kd

    def show(self):
        print("CurvePt({{:.3f}, {:.3f}, {:.3f}}, {:.3f}, {:.3f}, {:.3f})".format(self.pos.x, self.pos.y, self.pos.theta,
                                                                                 self.s, self.k, self.kd))


def lerp(a: CurvePt, b: CurvePt, t: float):
    return CurvePt(VecSE2.lerp(a.pos, b.pos, t), a.s + (b.s - a.s)*t, a.k + (b.k - a.k)*t, a.kd + (b.kd - a.kd)*t)


class CurveIndex:
    def __init__(self, i: int, t: float):
        self.i = i
        self.t = t


def curveindex_end(curve: list):
    return CurveIndex(len(curve)-1, 1.0)


CURVEINDEX_START = CurveIndex(1, 0.0)


class CurveProjection:
    def __init__(self, ind: CurveIndex, t: float, phi: float):
        self.ind = ind
        self.t = t
        self.phi = phi


def proj(posG: VecSE2.VecSE2, curve: list):  # TODO: adjust list index
    ind = index_closest_to_point(curve, posG)
    curveind = CurveIndex(0, None)
    footpoint = VecSE2(None, None, None)
    if 1 < ind < len(curve):
        t_lo = get_lerp_time(curve[ind - 1], curve[ind], posG)
        t_hi = get_lerp_time(curve[ind], curve[ind + 1], posG)

        p_lo = lerp(curve[ind - 1].pos, curve[ind].pos, t_lo)
        p_hi = lerp(curve[ind].pos, curve[ind + 1].pos, t_hi)

        d_lo = norm(VecE2(p_lo - posG))
        d_hi = norm(VecE2(p_hi - posG))
        if d_lo < d_hi:
            footpoint = p_lo
            curveind = CurveIndex(ind - 1, t_lo)
        else:
            footpoint = p_hi
            curveind = CurveIndex(ind, t_hi)
    elif ind == 1:
        t = get_lerp_time(curve[1], curve[2], posG)
        footpoint = lerp(curve[1].pos, curve[2].pos, t)
        curveind = CurveIndex(ind, t)
    else:  # ind == length(curve)
        t = get_lerp_time(curve[end - 1], curve[end], posG)
        footpoint = lerp(curve[end - 1].pos, curve[end].pos, t)
        curveind = CurveIndex(ind - 1, t)

    return get_curve_projection(posG, footpoint, curveind)


