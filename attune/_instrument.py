__all__ = ["Instrument"]


from datetime import datetime as _datetime
from typing import Dict
import json

from ._arrangement import Arrangement
from ._motor import Motor
from ._note import Note


class Instrument(object):
    def __init__(self, arrangements, motors, *, name=None, datetime=None):
        self._name: str = name
        self._arrangements: Dict["str", Arrangement] = arrangements
        self._motors: Dict["str", Motor] = motors
        if datetime is None:
            self.datetime = _datetime.utcnow()

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self._motors != other._motors:
            return False
        if self._arrangements != other._arrangements:
            return False
        return True

    def __call__(self, ind_value, arrangement_name=None) -> Note:
        # get correct arrangement
        valid = []
        for arrangement in self._arrangements.values():
            # we should probably do "close enough" for floating point on the edges...
            if arrangement.ind_min <= ind_value <= arrangement.ind_max:
                valid.append(arrangement)
        if len(valid) == 1:
            arrangement = valid[0]
        else:
            raise Exception("There are multiple valid arrangements! You must specify one.")
        # call arrangement
        motor_positions = {}
        todo = [(ind_value, tune) for tune in arrangement.tunes.items()]
        while todo:
            v, t = todo.pop(0)
            tune_name, tune = t
            if tune_name in self._motors:
                assert tune_name not in motor_positions
                motor_positions[tune_name] = tune(v)
            elif tune_name in self._arrangements:
                new = [(tune(v), tune) for tune in self._arrangements[tune_name].tunes.items()]
                todo += new
            else:
                raise ValueError(f"Unrecognized name {tune_name}")
        # finish
        note = Note(
            motors=self._motors,
            motor_positions=motor_positions,
            arrangement_name=arrangement.name,
        )
        return note

    def as_dict(self):
        out = {}
        out["name"] = self.name
        out["arrangements"] = {k: v.as_dict() for k, v in self._arrangements.items()}
        out["motors"] = {k: v.as_dict() for k, v in self._motors.items()}
        return out

    @property
    def name(self):
        return self._name

    def save(self, file):
        json.dump(self.as_dict(), file)
