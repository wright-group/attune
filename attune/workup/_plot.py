import WrightTools as wt
import matplotlib.pyplot as plt
import numpy as np


def plot_intensity(data, channel, dependent, curve, prior_curve=None):
    fig, gs = wt.artists.create_figure(
        width="double", nrows=2, cols=[1, "cbar"], default_aspect=.5
    )
    ax = plt.subplot(gs[0, 0])
    curve_plot_kwargs = {"lw": 4, "c": "k", "alpha": .75}
    prior_curve_plot_kwargs = {"lw": 2, "c": "k"}
    ax.plot(curve.setpoints[:], curve[dependent][:], **curve_plot_kwargs)
    if prior_curve:
        ax.plot(prior_curve.setpoints[:], prior_curve[dependent][:], **prior_curve_plot_kwargs)
    ax.set_ylabel(dependent)
    wt.artists.plot_gridlines()

    ax = plt.subplot(gs[1, 0])
    ax.pcolor(data, channel=channel)
    x.im = ax.get_xlim()
    if prior_curve:
        ypoints = (
            prior_curve(curve.setpoints[:], curve.setpoints.units, full=False)[dependent]
            - curve[dependent][:]
        )
    else:
        ypoints = curve[dependent][:]
    ax.plot(curve.setpoints[:], ypoints, **curve_plot_kwargs)
    ax.axhline(0, **prior_curve_plot_kwargs)
    wt.artists.plot_gridlines()
    ax.set_ylabel(r"$\mathsf{{\Delta {dependent}}}$".format(dependent=dependent))
    ax.set_xlabel(f"Setpoint ({curve.setpoints.units})")
    ax.set_xlim(xlim)

    cax = plt.subplot(gs[1, 1])
    ticks = np.linspace(data[channel].null, data[channel].max(), 11)
    wt.artists.plot_colorbar(
        cax, clim=(data[channel].null, data[channel].max()), ticks=ticks, label=channel
    )

    return fig, gs
