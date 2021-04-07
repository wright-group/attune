from .. import Instrument
from .. import Tune
from .. import Arrangement
import json
import os

file1 = "OpticalDevices.json"
file2 = "Motors.json"


def from_topas4(topas4_folder):
    """Convert a LightConversion marked up Topas4 calibration JSON file into an Instrument object.
    Topas4 Folder must contain at least the following 2 files:  OpticalDevices.json and Motors.json."""
    with open(os.path.join(topas4_folder, file1), "r") as f:
        jsond1 = json.load(f)

    with open(os.path.join(topas4_folder, file2), "r") as g:
        jsond2 = json.load(g)

    jsond1actID = jsond1.get("ActiveConfigurationGUID")
    jsond1sub = jsond1["Configurations"]

    ind = 0
    for a in range(len(jsond1sub)):
        if jsond1sub[a]["GUID"] == jsond1actID:
            ind = a

    jsond1sub2 = jsond1sub[ind]["OpticalDevices"]
    
    arrangements = {}
    
    for b in range(len(jsond1sub2)):

        jsond1sub3 = jsond1sub2[b]["Interactions"]
        jsond2sub = jsond2["Motors"]

        motorlist = list()
        for motor in jsond2sub:
            motorlist.append(motor["Title"])

        for jsond1sub3ind in jsond1sub3:
            arrange_name_full = jsond1sub3ind.get("Type")

            if ">" in arrange_name_full:
                arrange_name,parent=arrange_name_full.split(">",maxsplit=1)
            else:
                arrange_name=arrange_name_full
                parent=arrange_name_full.split("-", maxsplit=1)[-1]
                if arrange_name==parent:
                    parent=None
                    
                    
            tunes = {}

            if parent is not None:
                inputpoints = jsond1sub3ind.get("InputPoints")
                deparr = list()
                indarr = list()
                for inputpoint in inputpoints:
                    indarr.append(inputpoint.get("Input"))
                    deparr.append(inputpoint.get("Output"))
                
                tune = Tune(indarr, deparr)
                tunes[parent] = tune

            motors = jsond1sub3ind.get("MotorPositionCurves")
            for index in range(len(motors)):
                points = motors[index]
                motorindex=points["MotorIndex"]
                k = motorlist[motorindex]
                deparr = list()
                indarr = list()
                for point in points["Points"]:
                    indarr.append(point.get("Input"))
                    deparr.append(point.get("Output"))

                tune = Tune(indarr, deparr)
                tunes[k] = tune

            arrangements[arrange_name] = Arrangement(arrange_name, tunes)
            


    instr = Instrument(arrangements)

    return instr
