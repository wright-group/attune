__all__ = ["Note"]


from typing import Dict
from ._motor import Motor


class Note:
    def __init__(self, motors, motor_positions, arrangement_name, **kwargs):
        self.motors: Dict["str", Motor] = motors
        self.motor_positions: Dict["str", float] = motor_positions
        self.arrangement_name: str = arrangement_name
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getitem__(self, k):
        return self.motor_positions[k]
