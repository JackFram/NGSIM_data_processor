from Basic import Vehicle

class RecordFrame:
    def __init__(self, lo: int, hi: int):
        self.lo = lo
        self.hi = hi

    def __len__(self):
        return self.hi - self.lo + 1


class RecordState:
    def __init__(self, state: Vehicle.VehicleState, id: list):
        self.state = state  # Dict
        self.id = id  # Array


class ListRecord:
    def __init__(self, timestep: float, frames: list, states: list, defs: dict):
        """
        timestep::Float64
        frames::Vector{RecordFrame}
        states::Vector{RecordState}
        defs::Dict{I, D}

        """
        self.timestep = timestep
        self.frames = frames
        self.states = states
        self.defs = defs



