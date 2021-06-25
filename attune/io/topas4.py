from .. import Instrument
from .. import DiscreteTune
from .. import Tune
from .. import Arrangement
import json
import os

file1 = "OpticalDevices.json"
file2 = "Motors.json"


def from_topas4(topas4_folder):
    """Convert a LightConversion marked up Topas4 calibration JSON file into an Instrument object.
    Topas4 Folder must contain at least the following 2 files:  OpticalDevices.json and Motors.json."""
    with open(os.path.join(topas4_folder, "OpticalDevices.json"), "r") as f:
        opt_dev = json.load(f)

    with open(os.path.join(topas4_folder, "Motors.json"), "r") as g:
        motors = json.load(g)["Motors"]

    with open(os.path.join(topas4_folder, "SeparationDevices.json"), "r") as g:
        sep_dev = json.load(g)

    opt_dev_active_guid = opt_dev.get("ActiveConfigurationGUID")
    opt_dev_conf = opt_dev["Configurations"]

    ind = 0
    for a in opt_dev_conf:
        if a["GUID"] == opt_dev_active_guid:
            opt_dev_active = a["OpticalDevices"]
            break

    sep_dev_active_guid = sep_dev.get("ActiveConfigurationGUID")
    sep_dev_conf = sep_dev["Configurations"]

    ind = 0
    for a in sep_dev_conf:
        if a["GUID"] == sep_dev_active_guid:
            sep_dev_active = a["SeparationDevices"]
            break

    arrangements = {}

    for interaction in opt_dev_active:

        interaction = interaction["Interactions"]

        motorlist = {}
        for motor in motors:
            index = motor["Index"]
            motorlist[index] = motor["Title"]

        for independent in interaction:
            arrange_name_full = independent.get("Type")

            if ">" in arrange_name_full:
                arrange_name, parent = arrange_name_full.split(">", maxsplit=1)
            else:
                arrange_name = arrange_name_full
                parent = arrange_name_full.split("-", maxsplit=1)[-1]
                if arrange_name == parent:
                    parent = None

            tunes = {}

            if parent is not None:
                inputpoints = independent.get("InputPoints")
                deparr = []
                indarr = []
                for inputpoint in inputpoints:
                    indarr.append(inputpoint.get("Output"))
                    deparr.append(inputpoint.get("Input"))

                tune = Tune(indarr, deparr)
                tunes[parent] = tune

            ind_motors = independent.get("MotorPositionCurves")
            for points in ind_motors:
                motorindex = points["MotorIndex"]
                k = motorlist[motorindex]
                deparr = []
                indarr = []
                for point in points["Points"]:
                    indarr.append(point.get("Input"))
                    deparr.append(point.get("Output"))

                tune = Tune(indarr, deparr)
                tunes[k] = tune

            arrangements[arrange_name] = Arrangement(arrange_name, tunes).as_dict()

    # This section is not as flexible as the source, I believe...
    # Currently assumes all the positions are for one arrangement, given in full name
    # The source file accepts wildcards like `*` or `SH-*` that should be applied to all
    # matching arrangements, as well as points for a single motor applied to multiple/different
    # arrangement in the same json section.
    # However, for the simple example as in the test, this is good enough.
    # KFS 2021-06-25
    for interaction in sep_dev_active:
        for mot_position in interaction["MotorPositionCurves"]:
            mot_index = mot_position["Index"]
            mot_name = motorlist[mot_index]
            pos = {
                x["NamedPosition"]: (x["Input"]["From"], x["Input"]["To"])
                for x in mot_position["Points"]
            }
            tune = DiscreteTune(pos)

            arr = mot_position["Points"][0]["InteractionType"]

            arrangements[arr]["tunes"][mot_name] = tune

    instr = Instrument(arrangements)

    return instr
