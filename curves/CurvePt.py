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
