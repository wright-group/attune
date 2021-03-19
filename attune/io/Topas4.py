from .. import Instrument
import json


def fromTopas4(Topasfile):
    # converts a LightConversion marked up Topas4 calibration JSON file into 
    # an Instrument object
    f=open(Topasfile,'r')
    lines=f.read()
    f.close()
    jsond=json.loads(lines)

    return jsond


def toTopas4(Instrument):
    # converts an Instrument object to a LightConversion marked up
    # Topas4 JSON object, which can then be saved
    
    string=json.dumps(Instrument)

    return string