"""Function for processing multi-dependent tuning data."""

import itertools

import numpy as np
import scipy

import WrightTools as wt
from ._plot import plot_holistic
from ._common import save


__all__ = ["holistic"]


def _holistic(data, amplitudes, centers, curve):
    points = np.array([np.broadcast_to(a[:], amplitudes.shape).flatten() for a in data.axes]).T
    ndim = len(data.axes)
    delaunay = scipy.spatial.Delaunay(points)

    amp_interp = scipy.interpolate.LinearNDInterpolator(delaunay, amplitudes.points.flatten())
    cen_interp = scipy.interpolate.LinearNDInterpolator(delaunay, centers.points.flatten())

    # def
    out_points = []
    for p in curve.setpoints[:]:
        iso_points = []
        for s, pts, vals in _find_simplices_containing(delaunay, cen_interp, p):
            iso_points.extend(_edge_intersections(pts, vals, p))
        iso_points = np.array(iso_points)
        if len(iso_points) > 3:
            out_points.append(
                tuple(_fit_gauss(iso_points.T[i], amp_interp(iso_points)) for i in range(ndim))
            )
        else:
            out_points.append(tuple(np.nan for i in range(ndim)))

    return np.array(out_points)


def holistic(
    data,
    channels,
    dependents,
    curve,
    *,
    spectral_axis=-1,
    level=False,
    gtol=0.01,
    autosave=True,
    save_directory=None,
    **spline_kwargs,
):
    """Workup multi-dependent tuning data.

    Note:
    At this time, this function expects 2-dimensional motor space.
    The algorithm should generalize to N-dimensional motor space,
    however this is untested and plotting likely will fail.

    Parameters
    ----------
    data: WrightTools.Data
        The data object to process.
    channels: WrightTools.data.Channel or int or str or 2-tuple
        If singular: the spectral axis, from which the 0th and 1st moments will be taken to
        obtain amplitudes and centers. In this case, `spectral_axis` determines which axis is
        used to obtain the moments.
        If a tuple: (amplitudes, centers), then these channels will be used directly.
    dependents: tuple of str
        Names of the dependents to modify in the curve, in the same order as the axes of `data`.
    curve: attune.Curve
        Curve object to modify. Setpoints are determined from the curve.

    Keyword Parameters
    ------------------
    spectral_axis: WrightTools.data.Axis or int or str (default -1)
        The axis along which to take moments.
        Only applies if a single channel is given.
    level: bool (default False)
        Toggle leveling data. If two channels are given, only the amplitudes are leveled.
        If a single channel is given, leveling occurs before taking the moments.
    gtol: float (default 0.01)
        Global tolerance for rejecting noise level relative to the global maximum.
    autosave: bool (default True)
        Toggles saving of curve files and images.
    save_directory: Path-like (Defaults to current working directory)
        Specify where to save files.
    **spline_kwargs: 
        Extra arguments to pass to spline creation (e.g. s=0, k=1 for linear interpolation)
    """
    data = data.copy()

    if isinstance(channels, (str, wt.data.Channel)):
        if level:
            data.level(channels, 0, -3)
        if isinstance(spectral_axis, int):
            spectral_axis = data.axis_names[spectral_axis]
        elif isinstance(spectral_axis, wt.data.Axis):
            spectral_axis = spectral_axis.expression
        getattr(data, spectral_axis).convert(curve.setpoints.units)
        # take channel moments
        data.moment(
            axis=spectral_axis,
            channel=channels,
            resultant=wt.kit.joint_shape(*[a for a in data.axes if a.expression != spectral_axis]),
            moment=0,
        )
        data.moment(
            axis=spectral_axis,
            channel=channels,
            resultant=wt.kit.joint_shape(*[a for a in data.axes if a.expression != spectral_axis]),
            moment=1,
        )
        amplitudes = data.channels[-2]
        centers = data.channels[-1]
        data.transform(*[a for a in data.axis_expressions if a != spectral_axis])
    else:
        amplitudes, centers = channels
        if isinstance(amplitudes, (int, str)):
            amplitudes = data.channels[wt.kit.get_index(data.channel_names, amplitudes)]
        if isinstance(centers, (int, str)):
            centers = data.channels[wt.kit.get_index(data.channel_names, centers)]
        if level:
            data.level(amplitudes.natural_name, 0, -3)

    if gtol is not None:
        cutoff = amplitudes.max() * gtol
        amplitudes.clip(min=cutoff)
    centers[np.isnan(amplitudes)] = np.nan

    out_points = _holistic(data, amplitudes, centers, curve)
    splines = [wt.kit.Spline(curve.setpoints, vals, **spline_kwargs) for vals in out_points.T]

    new_curve = _gen_curve(curve, dependents, splines)

    fig, _ = plot_holistic(
        data,
        amplitudes.natural_name,
        centers.natural_name,
        dependents,
        new_curve,
        curve,
        out_points,
    )

    if autosave:
        save(new_curve, fig, "holistic", save_directory)
    return new_curve


def _gen_curve(curve, dependents, splines):
    new_curve = curve.copy()
    for dep, spline in zip(dependents, splines):
        new_curve[dep][:] = spline(new_curve.setpoints)
    new_curve.interpolate()
    return new_curve


def _find_simplices_containing(delaunay, interpolator, point):
    for s in delaunay.simplices:
        extrema = interpolator([p for p in delaunay.points[s]])
        if min(extrema) < point <= max(extrema):
            yield s, delaunay.points[s], extrema


def _edge_intersections(points, evaluated, target):
    sortord = np.argsort(evaluated)
    evaluated = evaluated[sortord]
    points = points[sortord]
    for (p1, p2), (v1, v2) in zip(
        itertools.combinations(points, 2), itertools.combinations(evaluated, 2)
    ):
        if v1 < target <= v2:
            yield tuple(
                p1[i] + (p2[i] - p1[i]) * ((target - v1) / (v2 - v1)) for i in range(len(p1))
            )


def _fit_gauss(x, y):
    x, y = wt.kit.remove_nans_1D(x, y)

    def resid(inps):
        nonlocal x, y
        return y - _gauss(*inps)(x)

    bounds = [(-np.inf, np.inf) for i in range(3)]
    x_range = np.max(x) - np.min(x)
    bounds[0] = (np.min(x) - x_range / 10, np.max(x) + x_range / 10)
    bounds = np.array(bounds).T
    x0 = [np.median(x), x_range / 10, np.max(y)]
    opt = scipy.optimize.least_squares(resid, x0, bounds=bounds)
    return opt.x[0]


def _gauss(center, sigma, amplitude):
    return lambda x: amplitude * np.exp(-1 / 2 * (x - center) ** 2 / sigma ** 2)
