import WrightTools as wt
import matplotlib.pyplot as plt
import numpy as np


def plot_intensity(data, channel, dependent, curve, prior_curve=None):
    fig, gs = wt.artists.create_figure(width="double", nrows=2, cols=[1, "cbar"])
    ax = plt.subplot(gs[0, 0])
    curve_plot_kwargs = {"lw": 4, "c": "k", "alpha": .75}
    prior_curve_plot_kwargs = {"lw": 2, "c": "k"}
    ax.plot(curve.setpoints, curve[dependent][:], **curve_plot_kwargs)
    if prior_curve:
        ax.plot(prior_curve.setpoints, prior_curve[dependent][:], **prior_curve_plot_kwargs)
    ax.set_ylabel(dependent)
    wt.artists.plot_gridlines()

    ax = plt.subplot(gs[1, 0])
    ax.pcolor(data, channel=channel)
    if prior_curve:
        ypoints = (
            prior_curve(curve.setpoints, curve.units, full=False)[
                wt.kit.get_index(prior_curve.dependent_names, dependent)
            ]
            - curve[dependent][:]
        )
    else:
        ypoints = curve[dependent][:]
    ax.plot(curve.setpoints, ypoints, **curve_plot_kwargs)
    ax.axhline(0, **prior_curve_plot_kwargs)
    wt.artists.plot_gridlines()
    ax.set_ylabel(r"$\mathsf{{\Delta {dependent}}}$".format(dependent=dependent))
    ax.set_xlabel(f"Setpoint ({curve.units})")

    cax = plt.subplot(gs[1, 1])
    ticks = np.linspace(data[channel].null, data[channel].max(), 11)
    wt.artists.plot_colorbar(
        cax, clim=(data[channel].null, data[channel].max()), ticks=ticks, label=channel
    )

    return fig, gs

def plot_tune_test(data, channel, curve, prior_curve, raw_offsets=None):
    fig, gs = wt.artists.create_figure(default_aspect=0.5, cols=[1, "cbar"])
    # heatmap
    ax = plt.subplot(gs[0, 0])
    ax.pcolor(data, channel=channel)
    ax.set_xlim(data.axes[0].min(), data.axes[0].max())
    # lines
    if raw_offsets is not None:
        ax.plot(curve.setpoints[:], raw_offsets, c="grey", lw=5, alpha=0.5)

    ax.plot(curve.setpoints[:], curve.setpoints[:] - prior_curve.setpoints[:] , c="k", lw=5, alpha=0.5)
    ax.axhline(c="k", lw=1)
    ax.grid()

    ax.set_xlabel(r"$\mathsf{{Setpoint, ({units})}}$".format(units=curve.setpoints.units))
    ax.set_ylabel(r"$\mathsf{{\Delta {symbol}}}$".format(symbol=wt.units.get_symbol(curve.setpoints.units)))

    # colorbar
    cax = plt.subplot(gs[:, -1])
    label = channel
    ticks = np.linspace(0, data[channel].max(), 7)
    wt.artists.plot_colorbar(cax=cax, label=label, ticks=ticks)

    return fig, gs
