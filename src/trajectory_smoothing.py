# Zhihao Zhang
# NGSIM dataset processor trajectory_smoothing.py file

class VehicleSystem:
    def __init__(self, process_noise: float = 0.077, observation_noise: float = 16.7,
                 control_noise_accel: float = 16.7, control_noise_turnrate: float = 0.46):
        delta_t = 0.1
        H = [[1.0, 0.0, 0.0, 0.0],
             [0.0, 1.0, 0.0, 0.0]]
        r = process_noise
        R = MvNormal(Matrix(Diagonal([r * 0.01, r * 0.01, r * 0.00001, r * 0.1])))  # process, TODO: tune this
        q = observation_noise
        Q = MvNormal(Matrix(Diagonal([q, q])))  # obs, TODO: tune this

        n_integration_steps = 10

        self.H = H
        self.R = R
        self.Q = Q
        self.delta_t = delta_t
        self.n_integration_steps = n_integration_steps
        self.control_noise_accel = control_noise_accel
        self.control_noise_turnrate = control_noise_turnrate