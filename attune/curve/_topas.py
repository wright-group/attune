import numpy as np
import pathlib
import warnings
from ._base import Curve
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
                curves[interaction].supercurves.append(c)
                c.interpolate()
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
        for key, value in curves.items():
            setattr(value, "siblings", [v for k, v in curves.items() if key != k])
            setattr(value, "supercurves", [])
        f.close()
        return curves

    def save(self, save_directory=None, plot=True, verbose=True, full=False):
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
        if full:
            to_insert = curve._get_family_dict()
        to_insert[interaction_string] = curve
        if interaction_string == "NON-NON-NON-Idl":
            to_insert["NON-NON-NON-Sig"] = _convert(curve)
            to_insert["NON-NON-NON-Sig"].interaction = "NON-NON-NON-Sig"
        if interaction_string == "NON-NON-NON-Sig":
            to_insert["NON-NON-NON-Idl"] = _convert(curve)
            to_insert["NON-NON-NON-Idl"].interaction = "NON-NON-NON-Idl"

        # get save directory
        if save_directory is None:
            save_directory = pathlib.Path()
        else:
            save_directory = pathlib.Path(save_directory)
        save_directory.mkdir(parents=True, exist_ok=True)
        timestamp = wt.kit.TimeStamp().path

        ret_name = curve.kind + "- " + timestamp
        ret_path = (save_directory / ret_name).with_suffix(".crv")

        if plot:
            image_path = ret_path.with_suffix(".png")
            title = ret_path.stem
            self.plot(autosave=True, save_path=image_path, title=title)

        while len(to_insert):
            curve = to_insert[list(to_insert.keys())[0]]
            out_name = curve.kind + "- " + timestamp
            out_path = (save_directory / out_name).with_suffix(".crv")
            all_sibs = [curve]
            if curve.siblings:
                all_sibs += curve.siblings

            with open(out_path, "w") as new_crv:
                _write_headers(new_crv, curve)
                new_crv.write(f"{len(all_sibs)}\n")
                for c in all_sibs:
                    c = to_insert.pop(c.interaction, c)
                    _write_curve(new_crv, c)
                if verbose:
                    print("curve saved at", out_path)

        return ret_path

    def _get_family_dict(self, start=None):
        if start is None:
            start = {}
        d = {k: v for k, v in start.items()}
        d.update({self.interaction: self})
        if self.siblings:
            for s in self.siblings:
                if s.interaction not in d:
                    d.update(s._get_family_dict(d))
        if self.subcurve:
            if self.subcurve.interaction not in d:
                d.update(self.subcurve._get_family_dict(d))
        if self.supercurves:
            for s in self.supercurves:
                if s.interaction not in d:
                    d.update(s._get_family_dict(d))
        return d


def _insert(curve):
    motor_indexes = curve.motor_indexes
    arr = np.empty((len(motor_indexes) + 3, len(curve.setpoints)))
    arr[0] = curve.source_setpoints[:]
    arr[1] = curve.setpoints[:]
    arr[2] = len(motor_indexes)
    for i, m in enumerate(motor_indexes):
        arr[3 + i] = next(d for d in curve.dependents.values() if d.index == m)[:]
    return arr.T


def _convert(curve):
    curve = curve.copy()
    curve.setpoints.positions = 1 / ((1 / curve.pump_wavelength) - (1 / curve.setpoints[:]))
    curve.polarization = "V" if curve.polarization == "H" else "H"
    return curve


def _write_headers(f, curve):
    f.write("600\n")
    if curve.kind in "OPA/NOPA":
        f.write("OPA/NOPA\n")
        f.write(f"{int(curve.kind=='NOPA')}\n")
        f.write(f"{int(curve.config.get('use grating equation', 0))}\n")
        f.write(f"{curve.config.get('grating motor index', -1)}\n")
        f.write(f"{curve.config.get('grating constant', 0)}\n")
        f.write(f"{curve.config.get('maximum grating position', 0)}\n")
    else:
        f.write(f"{curve.kind}\n")
    f.write(f"{len(curve.dependents)}\n")
    f.write("\t".join(str(i) for i in curve.motor_indexes))
    f.write("\n")


def _write_curve(f, curve):
    curve = curve.copy()
    curve.convert("nm")
    curve.sort()
    f.write(f"{curve.interaction}\n")
    if len(curve.comment) == 0 or curve.comment[-1] != "\n":
        curve.comment += "\n"
    num_lines = curve.comment.count("\n")
    f.write(f"{num_lines}\n")
    f.write(curve.comment)
    f.write(f"{int(curve.polarization=='H')}\n")
    f.write(f"{curve.pump_wavelength}\n")
    f.write(f"{len(curve.dependents)}\n")
    f.write("\t".join(str(i) for i in curve.offsets))
    f.write("\n")
    array = _insert(curve)
    f.write(f"{len(array)}\n")
    fmt = ["%0.6f"] * len(array.T)
    fmt[2] = "%0.f"  # this field is an int
    np.savetxt(f, array, fmt=fmt, delimiter="\t", newline="\n")
