from ._instrument import Instrument
from ._transition import Transition


def update_merge(base: Instrument, replace: Instrument) -> Instrument:
    """Update the base instrument with tunes from the replace instrument

    Name and any tunes not present in replace remain from base.
    Base is the instrument which is identified by the transition.
    If new arrangements are present in replace, they are added to base.
    """
    instr = base.as_dict()
    for arr_name, arr in replace.arrangements.items():
        if arr_name not in base.arrangements:
            instr["arrangements"][arr_name] = arr
            continue
        for tune_name, tune in arr.items():
            instr["arrangements"][arr_name]["tunes"][tune_name] = tune
    transition = Transition(type="update_merge", previous=base)
    instr.pop("transition", None)
    print(repr(transition))
    return Instrument(**instr, transition=transition)
