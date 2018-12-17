
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

def from_TOPAS_crvs(filepaths, kind, interaction_string):
    """Create a curve object from a TOPAS crv file.

    Parameters
    ----------
    filepaths : list of str [base, mixer 1, mixer 2, mixer 3]
        Paths to all crv files for OPA. Filepaths may be None if not needed /
        not applicable.
    kind : {'TOPAS-C', 'TOPAS-800'}
        The kind of TOPAS represented.
    interaction_string : str
        Interaction string for this curve, in the style of Light Conversion -
        e.g. 'NON-SF-NON-Sig'.

    Returns
    -------
    WrightTools.tuning.curve.Curve object
    """
    TOPAS_interactions = TOPAS_interaction_by_kind[kind]
    # setup to recursively import data
    interactions = interaction_string.split("-")
    interaction_strings = []  # most subservient tuning curve comes first
    idx = 3
    while idx >= 0:
        if not interactions[idx] == "NON":
            interaction_strings.append("NON-" * idx + "-".join(interactions[idx:]))
        idx -= 1
    # create curve objects, starting from most subservient curve
    subcurve = None
    for interaction_string in interaction_strings:
        # open appropriate crv
        interactions = interaction_string.split("-")
        curve_index = next((i for i, v in enumerate(interactions) if v != "NON"), -1)
        crv_path = filepaths[-(curve_index + 1)]
        with open(crv_path, "r") as crv:
            crv_lines = crv.readlines()
        # collect information from file
        for i in range(len(crv_lines)):
            if crv_lines[i].rstrip() == interaction_string:
                line_index = i + TOPAS_interactions[interaction_string][0]
                num_tune_points = int(crv_lines[line_index - 1])
        # get the actual array
        lis = []
        for i in range(line_index, line_index + num_tune_points):
            line_arr = np.fromstring(crv_lines[i], sep="\t")
            lis.append(line_arr)
        arr = np.array(lis).T
        # create the curve
        source_colors = Motor(arr[0], "source colors")
        colors = arr[1]
        motors = []
        for i in range(3, len(arr)):
            motor_name = TOPAS_interactions[interaction_string][1][i - 3]
            motor = Motor(arr[i], motor_name)
            motors.append(motor)
            name = wt.kit.filename_parse(crv_path)[1]
        curve = Curve(
            colors,
            "nm",
            motors,
            name,
            interaction_string,
            kind,
            method=Linear,
            subcurve=subcurve,
            source_colors=source_colors,
        )
        subcurve = curve.copy()
    # finish
    setattr(curve, "old_filepaths", filepaths)
    return curve





def to_TOPAS_crvs(curve, save_directory, kind, full, **kwargs):
    """Save a curve object.

    Parameters
    ----------
    curve : WrightTools.tuning.curve.Curve object
        Curve.
    save_directory : string.
        Save directory.
    kind : string
        Curve kind.
    full : boolean
        Toggle saving subcurves.
    **kwargs

    Returns
    -------
    string
        Output path.
    """
    TOPAS_interactions = TOPAS_interaction_by_kind[kind]
    # unpack
    curve = curve.copy()
    curve.convert("nm")
    old_filepaths = kwargs["old_filepaths"]
    interaction_string = curve.interaction
    # open appropriate crv
    interactions = interaction_string.split("-")
    curve_index = next((i for i, v in enumerate(interactions) if v != "NON"), -1)
    curve_index += 1
    curve_index = len(old_filepaths) - curve_index
    crv_path = old_filepaths[curve_index]
    if full:
        # copy other curves over as well
        for i, p in enumerate(old_filepaths):
            print(i, p, curve_index)
            if i == curve_index:
                continue
            if p is None:
                continue
            print(i, p)
            d = os.path.join(save_directory, os.path.basename(p))
            shutil.copy(p, d)
    with open(crv_path, "r") as crv:
        crv_lines = crv.readlines()
    # collect information from file
    for i in range(len(crv_lines)):
        if crv_lines[i].rstrip() == interaction_string:
            line_index = i + TOPAS_interactions[interaction_string][0]
