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

    jsond1actID=jsond1.get("ActiveConfigurationGUID")
    jsond1sub=jsond1["Configurations"]
    
    ind=0
    for a in range(len(jsond1sub)):
        if jsond1sub[a]["GUID"]==jsond1actID:
            ind=a

    jsond1sub2 = jsond1sub[ind]["OpticalDevices"]
    arrangements = {}
    for b in range(len(jsond1sub2)):    
    
        jsond1sub3 = jsond1sub2[b]["Interactions"]

        jsond2sub = jsond2["Motors"]

        motorlist = list()
        for motor in jsond2sub:
            motorlist.append(motor["Title"])

        

        for jsond1sub3ind in jsond1sub3:
            arrange_name = jsond1sub3ind.get("Type")
            motors = jsond1sub3ind.get("MotorPositionCurves")

            tunes = {}

            for index in range(len(motors)):
                k = motorlist[index]
                points = motors[index]

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
