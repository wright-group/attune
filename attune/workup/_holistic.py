"""Function for processing multi-dependent tuning data."""

import itertools
import pathlib

import numpy as np
import scipy

import WrightTools as wt


__all__ = ["holistic"]

def holistic(
    data,
    channel,
    dependents,
    curve,
    *,
    level=False,
    gtol=0.01,
    autosave=True,
    save_directory=None,
    **spline_kwargs,
):
    """Workup multi-dependent tuning data."""
    # TODO: docstring
    # HACKS
    # TODO extract data pre-worukup
    data = data.copy()
    axis="wa"
    # TODO: check if level does what we want
    if level:
        data.level(channel, 0, -3)

    # take channel moments 
    data.moment(axis=axis, channel=channel, resultant=wt.kit.joint_shape(*data.axes[:-1]), moment=0)
    data.moment(axis=axis, channel=channel, resultant=wt.kit.joint_shape(*data.axes[:-1]), moment=1)
    amplitudes = data.channels[-2]
    centers = data.channels[-1]
    data.transform(*[a for a in data.axis_expressions if a != axis])

    # TODO: decide whether tolerances are included in pre-workup or not
    cutoff = amplitudes.max() * gtol
    amplitudes.clip(min=cutoff)
    centers[np.isnan(amplitudes)] = np.nan

    # --- End of pre workup ---

    # TODO, make sure array axis isn't counted in "full" (use `np.broadcast_to`)
    points = list(zip(*[a.full[...,0].flatten() for a in data.axes]))
    ndim = len(data.axes)
    delaunay = scipy.spatial.Delaunay(points)

    amp_interp = scipy.interpolate.LinearNDInterpolator(delaunay, amplitudes.points.flatten())
    cen_interp = scipy.interpolate.LinearNDInterpolator(delaunay, centers.points.flatten())

    # def
    out_points = []
    for p in curve.setpoints[:]:
        iso_points = []
        for s, pts, vals in find_simplices_containing(delaunay, cen_interp, p):
            iso_points.extend(edge_intersections(pts, vals, p))
        iso_points = np.array(iso_points)
        if len(iso_points) > 3:
            out_points.append(tuple(fit_gauss(iso_points.T[i], amp_interp(iso_points)) for i in range(ndim)))
        else:
            out_points.append(tuple(np.nan for i in range(ndim)))

    out_points = np.array(out_points)

    print(out_points)

    splines = [wt.kit.Spline(curve.setpoints, vals, **spline_kwargs) for vals in out_points.T]
    
    # def gen_curve(curve, dependents, splines) -> curve
    new_curve = curve.copy()
    for dep, spline in zip(dependents, splines):
        curve[dep][:] = spline(curve.setpoints)
    curve.interpolate()

    if autosave:
        # Should define function that is shared among all workupscripts
        if save_directory is None:
            save_directory = "."
        save_directory = pathlib.Path(save_directory)
        curve.save(save_directory=save_directory, full=True)
    return curve


def find_simplices_containing(delaunay, interpolator, point):
    for s in delaunay.simplices:
        extrema = interpolator([p for p in delaunay.points[s]])
        if min(extrema) < point <= max(extrema):
            yield s, delaunay.points[s], extrema

def edge_intersections(points, evaluated, target):
    sortord = np.argsort(evaluated)
    evaluated = evaluated[sortord]
    points = points[sortord]
    for (p1, p2), (v1,v2) in zip(itertools.combinations(points,2), itertools.combinations(evaluated, 2)):
        if v1 < target <= v2:
            yield tuple(p1[i] + (p2[i]-p1[i])*((target - v1)/(v2-v1)) for i in range(len(p1)))

def fit_gauss(x, y):
    def resid(inps):
        nonlocal x, y
        return y - gauss(*inps)(x)

    opt = scipy.optimize.leastsq(resid, [np.median(x), (np.max(x) - np.min(x))/10, np.max(y)])
    return opt[0][0]

def gauss(center, sigma, amplitude):
    return lambda x: amplitude * np.exp(-1/2 * (x - center) ** 2 / sigma ** 2)
