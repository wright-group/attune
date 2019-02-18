import numpy as np
import pathlib
import shutil
import copy
from ._base import Curve, Linear
from ._dependent import Setpoints, Dependent
import WrightTools as wt

__all__ = ["TopasCurve"]

TOPAS_C_motor_names = {
    0: ["Crystal_1", "Delay_1", "Crystal_2", "Delay_2"],
    1: ["Mixer_1"],
    2: ["Mixer_2"],
    3: ["Mixer_3"],
}

# [num_between, motor_names]
TOPAS_C_interactions = {
    "NON-NON-NON-Sig": [8, TOPAS_C_motor_names[0]],
    "NON-NON-NON-Idl": [8, TOPAS_C_motor_names[0]],
    "NON-NON-SH-Sig": [11, TOPAS_C_motor_names[1]],
    "NON-SH-NON-Sig": [11, TOPAS_C_motor_names[2]],
    "NON-NON-SH-Idl": [11, TOPAS_C_motor_names[1]],
    "NON-NON-SF-Sig": [11, TOPAS_C_motor_names[1]],
    "NON-NON-SF-Idl": [11, TOPAS_C_motor_names[1]],
    "NON-SH-SH-Sig": [11, TOPAS_C_motor_names[2]],
    "SH-SH-NON-Sig": [11, TOPAS_C_motor_names[3]],
    "NON-SH-SH-Idl": [11, TOPAS_C_motor_names[2]],
    "SH-NON-SH-Idl": [11, TOPAS_C_motor_names[3]],
    "DF1-NON-NON-Sig": [10, TOPAS_C_motor_names[3]],
}

TOPAS_800_motor_names = {
    0: ["Crystal", "Amplifier", "Grating"],
    1: [""],
    2: [""],
    3: ["NDFG_Crystal", "NDFG_Mirror", "NDFG_Delay"],
}

# [num_between, motor_names]
TOPAS_800_interactions = {
    "NON-NON-NON-Sig": [8, TOPAS_800_motor_names[0]],
    "NON-NON-NON-Idl": [8, TOPAS_800_motor_names[0]],
    "DF1-NON-NON-Sig": [7, TOPAS_800_motor_names[3]],
    "DF2-NON-NON-Sig": [7, TOPAS_800_motor_names[3]],
}

TOPAS_interaction_by_kind = {"TOPAS-C": TOPAS_C_interactions, "TOPAS-800": TOPAS_800_interactions}


class TopasCurve(Curve):
    @classmethod
    def read(cls, filepaths, interaction_string):
        """Create a curve object from a TOPAS crv file.

        Parameters
        ----------
        filepaths : list of str [base, mixer 1, mixer 2, mixer 3]
            Paths to all crv files for OPA. Filepaths may be None if not needed /
            not applicable.
        interaction_string : str
            Interaction string for this curve, in the style of Light Conversion -
            e.g. 'NON-SF-NON-Sig'.

        Returns
        -------
        WrightTools.tuning.curve.TopasCurve object
        """
        return cls.read_all(filepaths)[interaction_string]

    @classmethod
    def read_all(cls, filepaths):
        curves = {}
        for f in filepaths:
            curves.update(cls._read_file(f))
        for i, c in curves.items():
            interaction = i.split("-")
            for j, part in enumerate(interaction):
                if part != "NON":
                    interaction[j] = "NON"
                    break
            interaction = "-".join(interaction)
            if interaction in curves:
                c.subcurve = curves[interaction]
        return curves

    @classmethod
    def _read_file(cls, filepath):
        ds = np.DataSource(None)
        f = ds.open(str(filepath), "rt")
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
            for _a in range(int(f.readline())):
                comment += f.readline()

            # TODO: Check H/V
            polarization = "H" if int(f.readline()) else "V"
            pump_wavelength = float(f.readline())
            f.readline()  # n_motors
            offsets = np.fromstring(f.readline(), dtype=float, sep="\t")
            npts = int(f.readline())
            strings = [f.readline().strip() for _ in range(npts)]
            arr = np.genfromtxt(strings, delimiter="\t", max_rows=npts, filling_values=np.nan).T
            source_setpoints = Dependent(arr[0], "source", "nm")
            setpoints = Setpoints(arr[1], "output", "nm")
            dependents = []
            for i in range(n_motors):
                name = str(motor_indexes[i])
                units = None
                dependents.append(Dependent(arr[i + 3], name, units, index=motor_indexes[i]))
            # TODO: figure out what namem should default to
            name = interaction_string
            curves[interaction_string] = cls(
                setpoints,
                dependents,
                name=name,
                interaction=interaction_string,
                kind=kind,
                source_setpoints=source_setpoints,
                polarization=polarization,
                pump_wavelength=pump_wavelength,
                config=config,
                motor_indexes=motor_indexes,
                comment=comment,
                offsets=offsets,
            )
        return curves

    def save(self, save_directory, full=True):
        """Save a curve object.

        Parameters
        ----------
        save_directory : string.
            Save directory.
        kind : string
            Curve kind.
        full : boolean
            Toggle saving subcurves.

        Returns
        -------
        string
            Output path.
        """
        # unpack
        curve = self.copy()
        curve.convert("nm")
        interaction_string = curve.interaction

        to_insert = {}
        if interaction_string == "NON-NON-NON-Idl":
            to_insert["NON-NON-NON-Sig"] = (
                _convert(_insert(curve), curve.pump_wavelength),
                not curve.polarization,
            )
        to_insert[interaction_string] = (_insert(curve), curve.polarization)
        if interaction_string == "NON-NON-NON-Sig":
            to_insert["NON-NON-NON-Idl"] = (
                _convert(_insert(curve), curve.pump_wavelength),
                not curve.polarization,
            )

        save_directory = pathlib.Path(save_directory)
        save_directory.mkdir(parents=True, exist_ok=True)
        timestamp = wt.kit.TimeStamp().path
        out_name = curve.name.split("-")[0] + "- " + timestamp
        out_path = (save_directory / out_name).with_suffix(".crv")

        with open(out_path, "w") as new_crv:
            new_crv.write("600\r\n")
            if curve.kind in "OPA/NOPA":
                new_crv.write("OPA/NOPA\r\n")
                new_crv.write(f"{int(curve.kind=='NOPA')}\r\n")
                new_crv.write(f"{int(curve.config.get('use grating equation', 0))}\r\n")
                new_crv.write(f"{curve.config.get('grating motor index', -1)}\r\n")
                new_crv.write(f"{curve.config.get('grating constant', 0)}\r\n")
                new_crv.write(f"{curve.config.get('maximum grating position', 0)}\r\n")
            else:
                new_crv.write(f"{curve.kind}\r\n")
            new_crv.write(f"{len(curve.dependents)}\r\n")
            new_crv.write("\t".join(str(i) for i in curve.motor_indexes))
            new_crv.write("\r\n")
            new_crv.write(f"{len(to_insert)}\r\n")
            for k, v in to_insert.items():
                array, polarization = v
                array = array.T
                new_crv.write(k + "\r\n")
                if curve.comment[-1] != "\n":
                    curve.comment += "\r\n"
                num_lines = curve.comment.count("\n")
                new_crv.write(f"{num_lines}\r\n")
                new_crv.write(curve.comment)
                new_crv.write(f"{int(polarization=='H')}\r\n")
                new_crv.write(f"{curve.pump_wavelength}\r\n")
                new_crv.write(f"{len(curve.dependents)}\r\n")
                new_crv.write("\t".join(str(i) for i in curve.offsets))
                new_crv.write("\r\n")
                new_crv.write(f"{len(array)}\r\n")
                fmt = ["%0.6f"] * len(array.T)
                fmt[2] = "%0.f"  # this field is an int
                np.savetxt(new_crv, array, fmt=fmt, delimiter="\t", newline="\r\n")
        return out_path


def _insert(curve):
    motor_indexes = curve.motor_indexes
    arr = np.empty((len(motor_indexes) + 3, len(curve.setpoints)))
    arr[0] = curve.source_setpoints[:]
    arr[1] = curve.setpoints[:]
    arr[2] = len(motor_indexes)
    print(motor_indexes)
    for i, m in enumerate(motor_indexes):
        arr[3 + i] = next(d for d in curve.dependents.values() if d.index == m)[:]
    return arr


def _convert(arr, sum_):
    arr = np.copy(arr)
    arr[1] = 1 / ((1 / sum_) - (1 / arr[1]))
    arr = arr[:, ::-1]
    return arr
