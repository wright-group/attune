__all__ = ["Setable"]

from typing import Union, Optional
from dataclasses import dataclass, asdict


@dataclass
class Setable:
    """Container for default positions for a independent variable (something "setable")

    Parameters
    ----------
    name: str
        The key for a independent variable
    default: str or float (optional)
        The default value for this independent variable.  Defaults to None (no default).
    """

    name: str
    default: Optional[Union[str, float]] = None

    def as_dict(self):
        return asdict(self)
