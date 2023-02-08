__all__ = ["from_topas4"]

import json
import os
import re

from .. import Arrangement
from .. import DiscreteTune
from .. import Instrument
from .. import Setable
from .. import Tune


def from_topas4(topas4_folder):
    """Convert a LightConversion marked up Topas4 calibration JSON file into an Instrument object.
    Topas4 Folder must contain at least the following 2 files:  OpticalDevices.json and Motors.json.
    """
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
    else:
        raise ValueError("Active optical device GUID not found")

    sep_dev_active_guid = sep_dev.get("ActiveConfigurationGUID")
    sep_dev_conf = sep_dev["Configurations"]

    ind = 0
    for a in sep_dev_conf:
        if a["GUID"] == sep_dev_active_guid:
            sep_dev_active = a["SeparationDevices"]
            break
    else:
        raise ValueError("Active separation device GUID not found")

    arrangements = {}
    setables = {}

    for interaction in opt_dev_active:
        motorlist = {}
        for motor in motors:
            index = motor["Index"]
            motorlist[index] = motor["Title"]

        neutral_positions = interaction["NeutralPositions"]
        for pos in neutral_positions:
            index = pos["MotorIndex"]
            mot_name = motorlist[index]
            if pos["UseNamedPositionToResolveValue"]:
                position = pos["NamedPosition"]
            else:
                position = pos["Position"]
            setables[mot_name] = Setable(mot_name, position)

        interaction = interaction["Interactions"]

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

    discrete_tunes = {x: {} for x in arrangements}
    for interaction in sep_dev_active:
        for mot_position in interaction["MotorPositionCurves"]:
            mot_index = mot_position["Index"]
            mot_name = motorlist[mot_index]
            for point in mot_position["Points"]:
                interaction = point["InteractionType"]
                interaction = interaction.replace("[", "")
                interaction = interaction.replace("]", "")
                interaction = interaction.replace("*", ".*")
                for arr, mots in discrete_tunes.items():
                    if re.match(interaction, arr):
                        x = mots.get(mot_name, {})
                        x[point["NamedPosition"]] = (point["Input"]["From"], point["Input"]["To"])
                        mots[mot_name] = x

    for arr, mots in discrete_tunes.items():
        for mot_name, pos in mots.items():
            tune = DiscreteTune(pos)
            arrangements[arr]["tunes"][mot_name] = tune

    instr = Instrument(arrangements, setables)

    return instr
