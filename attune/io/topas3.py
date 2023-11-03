__all__ = ["from_topas3"]

import numpy as np
import warnings

from attune._tune import Tune
from attune._arrangement import Arrangement
from attune._instrument import Instrument


def from_topas3(filepaths):
    """Create a curve object from a TOPAS crv file.

    Parameters
    ----------
    filepaths : list of path-like
        Paths to all crv files for OPA.

    Returns
    -------
    attune.Instrument
    """
    arrangements = {}
    for f in filepaths:
        arrangements.update(_read_file(f))
    return Instrument(arrangements)


def _read_file(filepath):
    with open(str(filepath), "rt") as f:
        head = f.readline().strip()
        if head != "600":
            warnings.warn(f"Unexpected header {head}, expected '600'")
        kind = f.readline().strip()
        config = {}
        if kind == "OPA/NOPA":
            kind = "OPA" if f.readline().strip() == "0" else "NOPA"
            config["use grating equation"] = f.readline().strip() == "1"
            config["grating motor index"] = int(f.readline())
            config["grating constant"] = float(f.readline())
            config["maximum grating position"] = float(f.readline())
        n_motors = int(f.readline())
        motor_indexes = np.fromstring(f.readline(), dtype=int, sep="\t")
        n_curves = int(f.readline().strip())
        curves = {}
        for _ in range(n_curves):
            interaction_string = f.readline().strip()
            comment = ""
            for _ in range(int(f.readline())):
                comment += f.readline()

            # TODO: Check H/V
            polarization = "H" if int(f.readline()) else "V"  # noqa
            pump_wavelength = float(f.readline())  # noqa
            f.readline()  # n_motors
            offsets = np.fromstring(f.readline(), dtype=float, sep="\t")  # noqa
            npts = int(f.readline())
            strings = [f.readline().strip() for _ in range(npts)]
            arr = np.genfromtxt(strings, delimiter="\t", max_rows=npts, filling_values=np.nan).T

            tunes = {}

            source_interaction = interaction_string.split("-")

            # Compute the source interaction string, flipping the first entry that is
            # not "NON" to "NON"
            for i, v in enumerate(source_interaction):
                if v != "NON":
                    source_interaction[i] = "NON"
                    break

            # Ignore the case of "NON-NON-NON-NON", which is just the pump source
            if any(v != "NON" for v in source_interaction):
                source_tune = Tune(arr[1], arr[0], units="nm")
                tunes["-".join(source_interaction)] = source_tune

            for i in range(n_motors):
                name = str(motor_indexes[i])
                tunes[name] = Tune(arr[1], arr[i + 3])

            curves[interaction_string] = Arrangement(interaction_string, tunes)
    return curves
