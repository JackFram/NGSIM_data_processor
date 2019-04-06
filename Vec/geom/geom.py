import math


def deltaangle(a, b):
    assert isinstance(a, int) or isinstance(a, float)
    assert isinstance(b, int) or isinstance(b, float)

    return math.atan(math.sin(b-a)/math.cos(b-a))


def lerp_angle(a, b, t):
    return a + deltaangle(a, b) * t


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))