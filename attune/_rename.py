__all__ = ["rename"]

from ._transition import Transition, TransitionType
from ._instrument import Instrument


def rename(instr: Instrument, name: str):
    """Rename an instrument.

    Note: this tranistion breaks the history, as the primary key changes.
    """
    trans = Transition(TransitionType.rename, metadata={"old_name": instr.name})
    new_instr = instr.as_dict()
    new_instr["transition"] = trans
    new_instr["name"] = name
    return Instrument(**new_instr)
