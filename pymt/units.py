import numpy as np


def transform_math_to_azimuth(angle, units="rad"):
    angle *= -1.0
    if units == "rad":
        angle += np.pi * 0.5
    else:
        angle += 90.0
    return angle


def transform_azimuth_to_math(angle, units="rad"):
    angle *= -1.0
    if units == "rad":
        angle += np.pi * 0.5
    else:
        angle += 90.0
    return angle
