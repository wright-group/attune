__all__ = ["Instrument"]


from typing import Dict
from ._arrangement import Arrangement
from ._motor import Motor
from ._note import Note


class Instrument(object):

    def __init__(self, arrangements, motors, *, name=None):
        self._name: str = name
        self._arrangements: Dict["str", Arrangement] = arrangements
        self._motors = Dict["str", Motor] = motors

    def __call__(self, ind_value, arrangement_name=None) -> Note:
        pass

    def save(self):
        raise NotImplementedError
