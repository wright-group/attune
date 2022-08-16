# attune

[![image](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Tools for tuning optical parametric amplifiers and multidimensional spectrometers. 

Documentation is available at <https://attune.wright.tools/en/latest/>.

# Overview

`attune` has three primary jobs:

1.  attune parses calibration data to find optimal motor positions
    ```
    # data has scans of a motor position ("OPA1_SHS_crystal") against a signal
    # ("signal") for a set of second harmonic signal color setpoints
    # ("opa_color")
    calibration_data = wt.open(path_to_data.wt5)
    calibration_data.transform("opa_color", "motor")
    args = {
        "data": calibration_data,
        "channel": "signal",
        "arrangement": "SHS",
        "tune": "SHS_crystal",
        "instrument": "OPA1",
    }
    tuned_opa1 = attune.intensity(**args)
    ```

2.  `attune` organizes optimal motor positions.  The motor positions are stored in a hierarchy of mappings.  Beginning at the lowest level:

    * Tune : a map of OPA color (the "independent") to positions of a single motor (the "dependent").  
        ```
        my_tune = attune.Tune(
            independent=[450, 600, 700],
            dependent=[3.225, 2.332, 1.987]
        )  # relate color to bbo angle
        ```

    * Arrangement : a collection of Tunes that define a concerted process (e.g. to generate idler photons, one might move several motors (`bbo`, `g1`, etc.))
        ```
        idler = attune.Arrangement("idler", dict(bbo=my_tune, g1=my_other_tune))
        ```

    * Instrument : a collection of Arrangements (e.g. an OPA may have signal and idler)
        ```
        my_opa = attune.Instrument({"idler": idler, "signal": signal}, name="opa1")
        ```

        Note: arrangements can be called as tunables if they exist in the same instrument.  This can allow nested naming
        ```
        shi = attune.Arrangement(Dict(
            idler = Tune(shi_colors, idler_colors), 
            sh_crystal = Tune(shi_colors, angles)
        )) 
        ```

3. `attune` stores motor mappings and remembers them through version tracking. 
    * save a new instrument (or update an existing one)
        ```
        attune.store(my_opa)
        ```

    * lookup a saved instrument (by name)
        ```
        attune.catalog()  # lists all saved instruments
        my_opa = attune.load("opa1")  # fetches the most recent version of the instrument
        my_previous_opa = attune.undo(my_opa) # fetches the previous version of the instrument
        my_old_opa = attune.load("opa1", time="yesterday")  # optional kwarg specifies the version by time of usage    
        ```


## Notes

* `attune` uses default units of nanometers ("nm") for its independent variables.
    _At this time, units cannot be changed, so alternate units must be handled externally_ (PRs are welcome!).
    WrightTools calibration data is automatically converted into "nm" units for parsing.


