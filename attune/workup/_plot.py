import WrightTools as wt
import matplotlib.pyplot as plt
import numpy as np

def plot_intensity(data, channel, motor, curve, prior_curve=None):
    fig, gs = wt.artists.create_figure(width="double", nrows=2, cols=[1, "cbar"])
    ax = plt.subplot(gs[0,0])
    curve_plot_kwargs = {"lw":4, "c":"k", "alpha":.75}
    prior_curve_plot_kwargs = {"lw":2, "c":"k"}
    ax.plot(curve.colors, curve[motor][:], **curve_plot_kwargs)
    if prior_curve:
        ax.plot(prior_curve.colors, prior_curve[motor][:], **prior_curve_kwargs)
    ax.set_ylabel(motor)

    ax = plt.subplot(gs[1,0])
    ax.pcolor(data, channel=channel)
    if prior_curve:
        ypoints = curve[motor][:] - prior_curve.get_motor_positions(curve.colors, curve.units, full=False)[wt.kit.get_index(prior_curve.motor_names, motor)]
    else:
        ypoints = curve[motor][:]
    ax.plot(curve.colors, ypoints, **curve_plot_kwargs)
    ax.hline(0, **prior_curve_plot_kwargs)
    ax.set_ylabel(f"$\Delta {motor}$")
    ax.set_xlabel(f"Setpoint ({curve.units})")

    cax = plt.subplot(gs[1, 1])
    wt.artists.plot_colorbar(cax, clim=(data[channel].null, data[channel].max()))

    return fig, gs
