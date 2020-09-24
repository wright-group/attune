import pathlib

import WrightTools as wt


def save(curve, fig, image_name, save_directory=None):
    if save_directory is None:
        save_directory = "."
    save_directory = pathlib.Path(save_directory)
    curve.save(save_directory=save_directory, full=True)
    # Should we timestamp the image?
    p = (save_directory / image_name).with_suffix(".png")
    wt.artists.savefig(p, fig=fig)
