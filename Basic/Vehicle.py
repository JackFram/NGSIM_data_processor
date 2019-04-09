from Vec import VecSE2
from Roadway import roadway

"""
Frenet
______
roadind: road index
s: distance along lane
t: lane offset, positive is to left. zero point is the centerline of the lane.
ϕ: lane relative heading
"""


class Frenet:
    def __init__(self, roadind: roadway.RoadIndex, s: float, t: float, phi: float):
        self.roadind = roadind
        self.s = s
        self.t = t
        self.phi = phi


class AgentClass:
    MOTORCYCLE = 1
    CAR = 2
    TRUCK = 3
    PEDESTRIAN = 4


"""
    Vehicle definition which contains a class and a bounding box.
"""


class VehicleDef:
    def __init__(self, class_: int = AgentClass.CAR, length_: int = 4.0, width_: int = 1.8):
        self.class_ = class_
        self.length_ = length_
        self.width_ = width_


NULL_VEHICLEDEF = VehicleDef(AgentClass.CAR, None, None)


class VehicleState:
    def __init__(self, posG: VecSE2.VecSE2, posF: Frenet, v: float):
        self.posG = posG
        self.posF = posF
        self.v = v

