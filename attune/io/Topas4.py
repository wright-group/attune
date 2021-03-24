from .. import Instrument
from .. import Tune
from .. import Arrangement
from typing import Dict, Union
import json
import numpy as np

def fromTopas4(Topasfile):
    # converts a LightConversion marked up Topas4 calibration JSON file into 
    # an Instrument object
    f=open(Topasfile,'r')
    lines=f.read()
    f.close()
    jsond=json.loads(lines)
    jsond1=jsond['Configurations'].pop()['OpticalDevices'].pop()
    instr_name=jsond1['Title']
    jsondsub=jsond1['Interactions']
    
    a=True
        
    arrangements={}

    while a:

        
        try:
            jsondsub1=jsondsub.pop()
            arrange_name=jsondsub1.get('Type')
            motors=jsondsub1.get('MotorPositionCurves')
            
            b=True
            
            tunes={}

            while (b):
                try:
                    motor=motors.pop()
                    k=motor.get('MotorTitle')
                    points=motor.get('Points')
                    
                    deparr=np.empty(0,dtype=float)
                    indarr=np.empty(0,dtype=float)
                    
                    
                    c=True
                    while c:
                        try:
                            point=points.pop()
                            indarr=np.append(indarr,point.get('Input'))
                            deparr=np.append(deparr,point.get('Output'))
                            
                        except IndexError:
                            c=False
                    
                    tune=Tune(indarr,deparr)
                    tunes[k]=Dict[k,Union[tune,dict]]
                        
                except IndexError:
                    b=False
            
            arrangements[arrange_name]=Arrangement(arrange_name, tunes)
            

        except IndexError:
            a=False

    instr=Instrument(arrangements)

    return instr

'''
def toTopas4(Instrument):
    # converts an Instrument object to a LightConversion marked up
    # Topas4 JSON object, which can then be saved
    
    string=json.dumps(Instrument)

    return string

'''
