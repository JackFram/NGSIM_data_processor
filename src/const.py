import os
DIR, filename = os.path.split(os.path.abspath(__file__))

FLOATING_POINT_REGEX = r'[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?'
METERS_PER_FOOT = 0.3048

NGSIM_TRAJDATA_PATHS = [
                        os.path.join(DIR, "../data/i101_trajectories-0750am-0805am.txt"),
                        os.path.join(DIR, "../data/i101_trajectories-0805am-0820am.txt"),
                        os.path.join(DIR, "../data/i101_trajectories-0820am-0835am.txt"),
                        os.path.join(DIR, "../data/i80_trajectories-0400-0415.txt"),
                        os.path.join(DIR, "../data/i80_trajectories-0500-0515.txt"),
                        os.path.join(DIR, "../data/i80_trajectories-0515-0530.txt"),
                       ]

ROADWAY_80 = open(io->read(io, MIME"text/plain"(), Roadway), os.path.join(DIR, "../data/ngsim_80.txt"), "r")
ROADWAY_101 = open(io->read(io, MIME"text/plain"(), Roadway), os.path.join(DIR, "../data/ngsim_101.txt"), "r")

TRAJDATA_PATHS = [os.path.join( DIR, "../data/trajdata_i101_trajectories-0750am-0805am.txt"),
                os.path.join( DIR, "../data/trajdata_i101_trajectories-0805am-0820am.txt"),
                os.path.join( DIR, "../data/trajdata_i101_trajectories-0820am-0835am.txt"),
                os.path.join( DIR, "../data/trajdata_i80_trajectories-0400-0415.txt"),
                os.path.join( DIR, "../data/trajdata_i80_trajectories-0500-0515.txt"),
                os.path.join( DIR, "../data/trajdata_i80_trajectories-0515-0530.txt")]

NGSIM_TIMESTEP = 0.1 # [sec]
SMOOTHING_WIDTH_POS = 0.5 # [s]