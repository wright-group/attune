def offset_by(instrument, arrangement, tune, amount):
    ...


def offset_to(instrument, arrangement, tune, destination, setpoint, setpoint_units="same"):
    offset = destination - instrument[arrangement][tune](setpoint, setpoint_units)
    offset_by(instrument, arrangement, tune, amount)
