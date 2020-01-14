import WrightTools as wt
import matplotlib.pyplot as plt
import numpy as np


def plot_intensity(data, channel, dependent, curve, prior_curve=None, raw_offsets=None):
    fig, gs = wt.artists.create_figure(
        width="single", nrows=2, cols=[1, "cbar"], default_aspect=0.5
    )
    ax = plt.subplot(gs[0, 0])
    curve_plot_kwargs = {"lw": 5, "c": "k", "alpha": 0.5}
    prior_curve_plot_kwargs = {"lw": 2, "c": "k"}
    ax.plot(curve.setpoints[:], curve[dependent][:], **curve_plot_kwargs)
    if prior_curve:
        ax.plot(
            prior_curve.setpoints[:], prior_curve[dependent][:], **prior_curve_plot_kwargs,
        )
    ax.set_ylabel(dependent)
    wt.artists.plot_gridlines()
    ax.set_xlim(*curve.get_limits())
    ax.xaxis.set_tick_params(label1On=False)

    ax = plt.subplot(gs[1, 0])
    graymap = "greyscale"
    ax.pcolor(data, channel=f"{channel}_orig", cmap=graymap)
    ax.pcolor(data, channel=channel)
    if prior_curve:
        ypoints = (
            curve[dependent][:]
            - prior_curve(curve.setpoints[:], curve.setpoints.units, full=False)[dependent]
        )
    else:
        ypoints = curve[dependent][:]

    if raw_offsets is not None:
        ax.plot(curve.setpoints[:], raw_offsets, c="grey", lw=5, alpha=0.5)

    ax.plot(curve.setpoints[:], ypoints, **curve_plot_kwargs)
    ax.axhline(0, **prior_curve_plot_kwargs)
    wt.artists.plot_gridlines()
    ax.set_ylabel(fr"$\mathsf{{\Delta {dependent}}}$")
    ax.set_xlabel(data.axes[0].label)
    ax.set_xlim(*curve.get_limits())

    cax = plt.subplot(gs[1, 1])
    ticks = np.linspace(data[channel].null, data[channel].max(), 11)
    wt.artists.plot_colorbar(
        cax, vlim=(data[channel].null, data[channel].max()), ticks=ticks, label=channel
    )

    return fig, gs


def plot_setpoint(data, channel, dependent, curve, prior_curve=None, raw_offsets=None):
    fig, gs = wt.artists.create_figure(
        width="single", nrows=2, cols=[1, "cbar"], default_aspect=0.5
    )
    ax = plt.subplot(gs[0, 0])
    curve_plot_kwargs = {"lw": 5, "c": "k", "alpha": 0.5}
    prior_curve_plot_kwargs = {"lw": 2, "c": "k"}
    ax.plot(curve.setpoints[:], curve[dependent][:], **curve_plot_kwargs)
    ax.set_xlim(*curve.get_limits())
    ax.xaxis.set_tick_params(label1On=False)
    if prior_curve:
        ax.plot(
            prior_curve.setpoints[:], prior_curve[dependent][:], **prior_curve_plot_kwargs,
        )
    ax.set_ylabel(dependent)
    wt.artists.plot_gridlines()

    ax = plt.subplot(gs[1, 0])
    # data[channel][:] -= data.axes[0][:]
    data[channel].signed = True
    limits = -0.05 * data[channel].mag(), 0.05 * data[channel].mag()
    ax.pcolor(data, channel=channel, vmin=limits[0], vmax=limits[1])
    ax.set_xlim(*curve.get_limits())
    ax.set_ylim(data.axes[1].min(), data.axes[1].max())
    if prior_curve:
        ypoints = (
            curve[dependent][:]
            - prior_curve(curve.setpoints[:], curve.setpoints.units, full=False)[dependent]
        )
    else:
        ypoints = curve[dependent][:]

    if raw_offsets is not None:
        ax.plot(curve.setpoints[:], raw_offsets, c="grey", lw=5, alpha=0.5)
    ax.plot(curve.setpoints[:], ypoints, **curve_plot_kwargs)
    ax.axhline(0, **prior_curve_plot_kwargs)
    wt.artists.plot_gridlines()
    ax.set_ylabel(fr"$\mathsf{{\Delta {dependent}}}$")
    ax.set_xlabel(data.axes[0].label)
    ax.set_xlim(*curve.get_limits())

    cax = plt.subplot(gs[1, 1])
    ticks = np.linspace(*limits, 11)
    wt.artists.plot_colorbar(cax, vlim=limits, ticks=ticks, label=channel, cmap="signed")

    return fig, gs


def plot_tune_test(data, channel, curve, used_offsets, raw_offsets=None):
    data = data.copy()
    data.convert("wn")
    curve = curve.copy()
    if curve.setpoints.units == "nm":
        used_offsets = used_offsets[::-1]
        if raw_offsets is not None:
            raw_offsets = raw_offsets[::-1]
    curve.convert("wn")
    fig, gs = wt.artists.create_figure(default_aspect=0.5, cols=[1, "cbar"])
    # heatmap
    ax = plt.subplot(gs[0, 0])
    ax.pcolor(data, channel=channel)
    ax.set_xlim(data.axes[0].min(), data.axes[0].max())
    # lines
    if raw_offsets is not None:
        ax.plot(curve.setpoints[:], raw_offsets, c="grey", lw=5, alpha=0.5)

    ax.plot(
        curve.setpoints[:], used_offsets, c="k", lw=5, alpha=0.5,
    )
    ax.axhline(c="k", lw=1)
    ax.grid()

    ax.set_xlabel(data.axes[0].label)
    ax.set_ylabel(fr"$\mathsf{{\Delta}}$ {data.axes[0].label}")

    # colorbar
    cax = plt.subplot(gs[:, -1])
    label = channel
    ticks = np.linspace(0, data[channel].max(), 7)
    wt.artists.plot_colorbar(cax=cax, label=label, ticks=ticks)

    return fig, gs


def plot_holistic(
    data, amp_channel, center_channel, dependents, curve, prior_curve, raw_offsets=None
):
    data[amp_channel].normalize()

    amp_cmap = wt.artists.colormaps["default"]
    center_cmap = wt.artists.colormaps["rainbow"]

    fig, gs = wt.artists.create_figure(nrows=2, cols=[1, "cbar"])
    ax_amp = plt.subplot(gs[0, 0])
    ax_cen = plt.subplot(gs[1, 0])

    cax_amp = plt.subplot(gs[0, 1])
    cax_center = plt.subplot(gs[1, 1])
    amp_ticks = np.linspace(0, 1, 11)
    center_ticks = curve.setpoints

    ax_amp.pcolor(data, channel=amp_channel, cmap=amp_cmap)
    ax_amp.contour(
        data,
        channel=center_channel,
        levels=sorted(center_ticks),
        cmap=center_cmap,
        linewidths=2,
        alpha=1,
        vmin=np.min(center_ticks),
        vmax=np.max(center_ticks),
    )
    ax_cen.pcolor(
        data,
        channel=center_channel,
        cmap=center_cmap,
        vmin=np.min(center_ticks),
        vmax=np.max(center_ticks),
    )
    ax_cen.contour(
        data, channel=amp_channel, levels=amp_ticks, cmap=amp_cmap, linewidths=2, alpha=1,
    )

    wt.artists.set_fig_labels(xlabel=data.axes[0].label, ylabel=data.axes[1].label)

    wt.artists.plot_colorbar(cax_amp, cmap=amp_cmap, ticks=amp_ticks, label="Intensity")
    wt.artists.plot_colorbar(cax_center, cmap=center_cmap, ticks=center_ticks, label="Center")
    cax_center.set_xlabel("")

    for i in range(2):
        axis = np.array(np.broadcast_to(data.axes[i][:], data[amp_channel].shape))
        axis[np.isnan(data[amp_channel])] = np.nan

        amin = min(
            np.min(curve[dependents[i]]), np.min(prior_curve[dependents[i]]), np.nanmin(axis),
        )
        amax = max(
            np.max(curve[dependents[i]]), np.max(prior_curve[dependents[i]]), np.nanmax(axis),
        )
        arange = amax - amin
        amin -= arange * 0.05
        amax += arange * 0.05
        if i == 0:
            ax_amp.set_xlim((amin, amax))
            ax_cen.set_xlim((amin, amax))
        else:
            ax_amp.set_ylim((amin, amax))
            ax_cen.set_ylim((amin, amax))

    for ax in [ax_amp, ax_cen]:
        ax.plot(
            prior_curve[dependents[0]],
            prior_curve[dependents[1]],
            color="k",
            linewidth=2,
            zorder=2,
        )
        ax.plot(
            curve[dependents[0]],
            curve[dependents[1]],
            color="k",
            linewidth=6,
            alpha=0.5,
            zorder=2,
        )
        if raw_offsets is not None:
            ax.scatter(
                raw_offsets[:, 0], raw_offsets[:, 1], color="w", s=50, zorder=10, marker="*",
            )  # TODO don't be bad about point handleing

    return fig, gs
