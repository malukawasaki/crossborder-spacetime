"""Paper and supplementary figures, drawn from the committed tables in results/tables."""
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Patch

from .. import config, io, spacetime
from ..stations import cluster_lonlat, station_lonlat
from . import maps
from .style import save

GATEWAY_STATION_NAME = {"Kranji": "Kranji", "Marsiling": "Marsiling", "Woodlands": "Woodlands"}
ARC_BEND = {"Kranji": -0.12, "Marsiling": -0.24, "Woodlands": 0.12}
LW_MAX = 11.0  # line width (pt) of the largest flow on Figure 1


def _hour_axis(ax):
    ax.set_xlim(-0.5, 23.5)
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(0, 24, 2)], fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v / 1000:,.0f}k"))
    ax.grid(axis="y", alpha=0.6)
    ax.spines[["top", "right"]].set_visible(False)


# --------------------------------------------------------------------------- Figure 1
def fig1_sector_dispersal_map():
    crossings = io.read_table("stage1_causeway_crossings")
    split = io.read_table("stage1_feeder_split_46109")
    ind = io.read_table("stage1_industrial_clusters")
    sectors = io.read_table("stage2_gateway_sector")

    trunk = float(crossings.query("direction == 'JB -> SG' and day_type == 'ALL'").trips_per_month.iloc[0])
    feeders = split.query("day_type == 'ALL'").set_index("destination_group").trips_per_month
    pairs = sectors[(sectors.gateway != "Total") & (sectors.sector != "Other")]
    scale = LW_MAX / trunk  # one linear scale (pt per monthly trip) for every line on the map

    def lw(v):
        return max(0.6, v * scale)

    fig, ax = plt.subplots(figsize=(17, 9.5))
    maps.add_landuse(ax)
    jb, cp = maps.merc(*config.COORDS["JB CIQ"]), maps.merc(*config.COORDS["Woodlands Checkpoint"])

    ax.plot([jb[0], cp[0]], [jb[1], cp[1]], color="#ef4444", lw=lw(trunk) * 2.2, alpha=0.25, zorder=4)
    ax.plot([jb[0], cp[0]], [jb[1], cp[1]], color="#b91c1c", lw=lw(trunk), zorder=5, solid_capstyle="round")

    gw_xy = {}
    for name in config.GATEWAYS:
        gw_xy[name] = maps.merc(*station_lonlat(GATEWAY_STATION_NAME[name]))
        ax.plot([cp[0], gw_xy[name][0]], [cp[1], gw_xy[name][1]], color="#0f172a", lw=lw(feeders[name]),
                ls="--", zorder=6)

    for _, r in ind[ind.trips > 0].iterrows():
        x, y = maps.merc(*cluster_lonlat(r.stops.split()))
        ax.plot([cp[0], x], [cp[1], y], color="#581c87", lw=lw(r.trips_per_month), zorder=6)
        ax.scatter(x, y, s=150, marker="^", color="#581c87", edgecolors="white", linewidths=1.5, zorder=12)

    for _, r in pairs.sort_values("trips").iterrows():
        target = maps.merc(*config.SECTOR_COORDS[r.sector])
        ax.add_patch(FancyArrowPatch(gw_xy[r.gateway], target, connectionstyle=f"arc3,rad={ARC_BEND[r.gateway]}",
                                     color=config.SECTOR_COLOURS[r.sector], lw=lw(r.trips_per_month),
                                     arrowstyle="-", alpha=0.92, zorder=7))
    for sector, lonlat in config.SECTOR_COORDS.items():
        x, y = maps.merc(*lonlat)
        ax.scatter(x, y, s=160, color=config.SECTOR_COLOURS[sector], edgecolors="white", linewidths=2, zorder=9)

    ax.scatter(*cp, s=180, marker="D", color="#b91c1c", edgecolors="white", linewidths=2, zorder=15)
    ax.scatter(*jb, s=240, marker="o", color="#991b1b", edgecolors="white", linewidths=2.2, zorder=16)
    for name, g in config.GATEWAYS.items():
        ax.scatter(*gw_xy[name], s=250, marker="s", color="#0f172a", edgecolors="white", linewidths=1.8, zorder=14)
        ax.text(*gw_xy[name], g["letter"], color="white", fontsize=9.5, fontweight="bold", ha="center",
                va="center", zorder=15)

    x0, y0 = maps.merc(config.MAP_EXTENT[0], config.MAP_EXTENT[2])
    x1, y1 = maps.merc(config.MAP_EXTENT[1], config.MAP_EXTENT[3])
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    maps.add_basemap(ax)

    ref = 100_000
    legend = [
        Line2D([0], [0], color="#b91c1c", lw=4, label=f"Causeway bus crossings JB → SG ({trunk / 1e3:,.0f}k/month)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#991b1b", markersize=10, label="JB CIQ"),
        Line2D([0], [0], marker="D", color="w", markerfacecolor="#b91c1c", markersize=8,
               label="Woodlands Checkpoint"),
        Line2D([0], [0], color="#0f172a", lw=1.8, ls="--", label="Stage 1 bus feeder to gateway"),
        Line2D([0], [0], marker="^", color="w", markerfacecolor="#581c87", markersize=10,
               label="Direct bus to industrial-area stops"),
        *[Line2D([0], [0], color=c, lw=3, label=f"Stage 2 rail, weekday AM peak: {s}")
          for s, c in config.SECTOR_COLOURS.items() if s != "Other"],
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#0f172a", markersize=10,
               label="Gateways: A Kranji, B Marsiling, C Woodlands"),
        Line2D([0], [0], color="#64748b", lw=lw(ref), label=f"Line width key: {ref / 1e3:,.0f}k trips/month"),
        *[Patch(facecolor=c, alpha=0.55, label=f"MP2019: {k}") for k, c in config.LANDUSE_COLOURS.items()],
    ]
    ax.legend(handles=legend, fontsize=7.5, loc="upper left", bbox_to_anchor=(0.015, 0.98), framealpha=0.95,
              edgecolor="#94a3b8", labelspacing=0.38)
    ax.set_title("Cross-border mobility continuum: Causeway crossing, bus feeder (Stage 1) and rail "
                 "dispersal by functional sector (Stage 2)", fontsize=13, fontweight="bold", pad=12)
    ax.set_axis_off()
    save(fig, "fig1_sector_dispersal_map")


# --------------------------------------------------------------------------- Figure 2
def fig2_spacetime_time_poverty():
    prof = spacetime.load_profiles()
    nodes = {k: v for k, v in prof["corridor_km"].items() if k in
             ("JB Home", "JB CIQ", "Woodlands Checkpoint", "Kranji MRT", "Orchard")}
    seg_min = {tuple(k.split("|")): v for k, v in prof["segment_minutes"].items()}
    seg_min.update({(b, a): v for (a, b), v in list(seg_min.items())})
    wps = prof["representative"]["waypoints"]
    causeway_km = nodes["Woodlands Checkpoint"] - nodes["JB CIQ"]
    causeway_min = seg_min[("JB CIQ", "Woodlands Checkpoint")]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9.8), gridspec_kw={"width_ratios": [1, 2.0]})
    fig.subplots_adjust(wspace=0.14, left=0.04, right=0.97, top=0.91, bottom=0.15)

    # Left: space-time line (distance vs time of day)
    ax1.axhspan(0, 4.5, color="#f8fafc", zorder=0)
    ax1.axhspan(4.5, 9.5, color="#fef2f2", alpha=0.6, zorder=0)
    ax1.axhspan(8.5, 18.0, xmin=0.86, xmax=1.0, color="#fffbeb", alpha=0.9, zorder=0)
    ax1.text(nodes["Orchard"] - 0.8, 13.25, "WORK", fontsize=11.5, color="#334155", ha="right", va="center",
             fontweight="bold", zorder=8)
    ax1.axhspan(17.0, 22.0, color="#fef2f2", alpha=0.6, zorder=0)
    ax1.axhspan(22.5, 24.0, color="#f8fafc", zorder=0)
    ax1.axvspan(nodes["JB CIQ"], nodes["Woodlands Checkpoint"], color="#ef4444", alpha=0.12, zorder=0)
    for xv in nodes.values():
        ax1.axvline(xv, color="#cbd5e1", lw=1.0, zorder=1)
    for h in range(25):
        ax1.axhline(h, color="#94a3b8" if h % 2 == 0 else "#cbd5e1", lw=0.8 if h % 2 == 0 else 0.5,
                    ls="-" if h % 2 == 0 else ":", zorder=1)
    for s in spacetime.segments(wps):
        x = [nodes[s["from"]], nodes[s["to"]]]
        y = [s["t0"], s["t1"]]
        if s["stationary"]:
            ax1.plot(x, y, color="#475569", lw=4.5, solid_capstyle="round", zorder=4)
            continue
        m = seg_min.get((s["from"], s["to"]), s["minutes"])
        ax1.plot(x, y, color=spacetime.time_colour(m), lw=6.0 if m > 60 else 4.2, solid_capstyle="round", zorder=4)
        if m > 60:
            ax1.plot(x, y, color="#ef4444", lw=18, alpha=0.18, zorder=3)
    for name, t in wps:
        ax1.scatter(nodes[name], t, s=55, color="#0f172a", edgecolors="white", linewidths=1.5, zorder=5)
    cx_mid = (nodes["JB CIQ"] + nodes["Woodlands Checkpoint"]) / 2
    ax1.annotate(f"Causeway\n{causeway_km:.2f} km | {causeway_min} min", xy=(cx_mid, 6.75),
                 xytext=(nodes["Woodlands Checkpoint"] + 1.2, 2.8), fontsize=11, color="#b91c1c",
                 fontweight="bold", ha="left", va="center",
                 bbox=dict(boxstyle="round,pad=0.45", facecolor="white", edgecolor="#ef4444", lw=1.5),
                 arrowprops=dict(arrowstyle="->", color="#ef4444", lw=1.6, connectionstyle="arc3,rad=-0.1"),
                 zorder=9)
    ax1.set_xlim(-3.5, max(nodes.values()) + 3.5)
    ax1.set_ylim(0, 24)
    ax1.invert_yaxis()
    ax1.set_xticks([])
    ticks = [("JB Home", "JB Home", 24.5, "right"), ("JB CIQ", "JB CIQ", 25.7, "center"),
             ("Woodlands Checkpoint", "Woodlands", 24.5, "left"), ("Kranji MRT", "Kranji MRT", 25.7, "center"),
             ("Orchard", "Orchard", 24.5, "center")]
    for key, label, y, ha in ticks:
        x = nodes[key]
        ax1.text(x, y, f"{label}\n({x:g} km)", fontsize=11.5, fontweight="bold", ha=ha, va="top", zorder=9)
        ax1.plot([x, x], [24.0, y - 0.1], color="#475569", lw=1.4, clip_on=False, zorder=8)
    ax1.set_yticks(range(0, 25, 2))
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):02d}:00"))
    ax1.tick_params(axis="y", labelsize=11.5)
    ax1.set_title("Space-Time Line Graph (24-Hour Profile)", fontsize=15.5, pad=14)
    ax1.spines[["top", "right", "left", "bottom"]].set_color("#64748b")

    # Right: the same journey on the map
    xy = {k: maps.merc(*config.COORDS[k]) for k in nodes}
    legs = [("JB Home", "JB CIQ"), ("JB CIQ", "Woodlands Checkpoint"), ("Woodlands Checkpoint", "Kranji MRT"),
            ("Kranji MRT", "Orchard")]
    for a, b in legs:
        m = seg_min[(a, b)]
        line = [xy[a][0], xy[b][0]], [xy[a][1], xy[b][1]]
        ax2.plot(*line, color=spacetime.time_colour(m), lw=8.0 if m > 60 else 5.0, alpha=0.95, zorder=4,
                 solid_capstyle="round")
        if m > 60:
            ax2.plot(*line, color="#ef4444", lw=22, alpha=0.22, zorder=3)
            mx, my = (xy[a][0] + xy[b][0]) / 2, (xy[a][1] + xy[b][1]) / 2
            ax2.annotate(f"Causeway Bottleneck\n{causeway_km:.2f} km | {m} min queue", xy=(mx, my),
                         xytext=(mx + 2800, my + 1400), fontsize=11.5, color="#b91c1c", fontweight="bold",
                         bbox=dict(boxstyle="round,pad=0.45", facecolor="white", edgecolor="#ef4444", lw=1.8),
                         arrowprops=dict(arrowstyle="->", color="#ef4444", lw=1.8), zorder=9)
    label_offsets = {"JB Home": (-800, 800, "right"), "JB CIQ": (-1100, -350, "right"),
                     "Woodlands Checkpoint": (800, -450, "left"), "Kranji MRT": (-700, -700, "right"),
                     "Orchard": (700, -450, "left")}
    for name, (x, y) in xy.items():
        red, kranji = name in ("JB CIQ", "Woodlands Checkpoint"), name == "Kranji MRT"
        ax2.scatter(x, y, s=120 if (red or kranji) else 85, zorder=6, edgecolors="white", linewidths=2,
                    color="#ef4444" if red else ("#0284c7" if kranji else "#0f172a"))
        dx, dy, ha = label_offsets[name]
        ax2.annotate(name, xy=(x, y), xytext=(x + dx, y + dy), fontsize=12, fontweight="bold", ha=ha, zorder=8,
                     bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#334155", alpha=0.96, lw=1.4))
    xs, ys = [p[0] for p in xy.values()], [p[1] for p in xy.values()]
    y0, y1 = min(ys) - 3500, max(ys) + 3500
    half_w = (y1 - y0) * (20.0 * (2.0 / 3.0) * 0.92) / (9.8 * 0.81) / 2
    cx = (min(xs) + max(xs)) / 2
    ax2.set_xlim(cx - half_w, cx + half_w)
    ax2.set_ylim(y0, y1)
    ax2.set_aspect("equal", adjustable="box")
    if not maps.add_basemap(ax2):
        maps.add_landuse(ax2, 0.35, 0.25)
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(maps.lon_label))
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(maps.lat_label))
    ax2.tick_params(labelsize=11.5)
    ax2.set_xlabel("Longitude (°E)", fontsize=13.5, fontweight="bold", labelpad=10)
    ax2.set_ylabel("Latitude (°N)", fontsize=13.5, fontweight="bold", labelpad=10)
    ax2.set_title("Space-Time Lines Map (Commute Journey)", fontsize=15.5, pad=14)
    ax2.spines[["top", "right", "left", "bottom"]].set_color("#64748b")

    legend = [Line2D([0], [0], color=spacetime.time_colour(90), lw=5, label="> 60 min (Causeway queue)"),
              Line2D([0], [0], color=spacetime.time_colour(35), lw=4, label="30–45 min (MRT leg)"),
              Line2D([0], [0], color=spacetime.time_colour(15), lw=4, label="10–20 min (Bus / Drive leg)"),
              Line2D([0], [0], color="#475569", lw=4, label="Work hours (at destination)")]
    fig.legend(handles=legend, loc="lower center", ncol=4, fontsize=12, framealpha=0.98, edgecolor="#94a3b8",
               bbox_to_anchor=(0.5, 0.01))
    fig.suptitle("Cross-Border Commute: Visualizing Time Poverty", fontsize=18, fontweight="bold", y=0.98)
    save(fig, "fig2_spacetime_time_poverty")


# --------------------------------------------------------------------------- Supplementary
def figS1_checkpoint_hourly():
    h = io.read_table("rhythms_checkpoint_hourly")
    fig, axes = plt.subplots(1, 2, figsize=(16, 5.5), sharey=True)
    for ax, (day, title) in zip(axes, [("WEEKDAY", "Weekdays"), ("WEEKENDS/HOLIDAY", "Weekends & holidays")]):
        d = h[h.day_type == day]
        ax.plot(d.hour, d.jb_to_sg_crossings, color=config.DIRECTION_COLOURS["JB -> SG"], lw=2.5, marker="o",
                ms=4, label="JB → SG: bus 46219 → 46109")
        ax.plot(d.hour, d.sg_to_jb_crossings, color=config.DIRECTION_COLOURS["SG -> JB"], lw=2.5, marker="o",
                ms=4, label="SG → JB: bus 46101 → 46211")
        ax.axvspan(5, 9, color="#f59e0b", alpha=0.08, zorder=0)
        ax.axvspan(17, 21, color="#6366f1", alpha=0.08, zorder=0)
        _hour_axis(ax)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_xlabel("Hour of day (h = h:00–h:59)")
    axes[0].set_ylabel("Bus trips across the Causeway (Jun 2025–Mar 2026)")
    axes[0].legend(fontsize=9.5, loc="upper right")
    fig.suptitle("Figure S1. Causeway bus crossings by hour and direction", fontsize=14, fontweight="bold")
    fig.tight_layout()
    save(fig, "figS1_checkpoint_hourly")


def figS2_top10_per_gateway():
    top = io.read_table("stage2_top10_per_gateway")
    fig, axes = plt.subplots(1, 3, figsize=(21, 5.4))
    fig.subplots_adjust(left=0.01, right=0.99, wspace=0.03, top=0.86, bottom=0.1)
    vmax = top.trips.max()
    x0, y0 = maps.merc(103.62, 1.26)
    x1, y1 = maps.merc(103.99, 1.47)
    for ax, (gw, g) in zip(axes, config.GATEWAYS.items()):
        maps.add_landuse(ax, 0.35, 0.25)
        o = maps.merc(*station_lonlat(gw))
        sub = top[top.gateway == gw].sort_values("trips")
        for _, r in sub.iterrows():
            ll = station_lonlat(r.destination)
            if ll is None:
                continue
            d = maps.merc(*ll)
            ax.add_patch(FancyArrowPatch(o, d, connectionstyle="arc3,rad=-0.15", arrowstyle="-",
                                         color=config.SECTOR_COLOURS[r.sector], lw=0.8 + 7 * r.trips / vmax,
                                         alpha=0.9, zorder=5))
            ax.scatter(*d, s=40, color=config.SECTOR_COLOURS[r.sector], edgecolors="white", zorder=6)
            ax.annotate(f"{int(r['rank'])}. {r.destination}", d, xytext=(4, 4), textcoords="offset points",
                        fontsize=7.5, zorder=7)
        ax.scatter(*o, s=220, marker="s", color="#0f172a", edgecolors="white", zorder=8)
        ax.text(*o, g["letter"], color="white", fontsize=9, fontweight="bold", ha="center", va="center", zorder=9)
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
        ax.set_aspect("equal")
        ax.set_axis_off()
        ax.set_title(f"Gateway {g['letter']}: {gw} ({g['station']})", fontsize=12, fontweight="bold")
    handles = [Line2D([0], [0], color=c, lw=3, label=s) for s, c in config.SECTOR_COLOURS.items()]
    fig.legend(handles=handles, loc="lower center", ncol=6, fontsize=9.5, frameon=False)
    fig.suptitle("Figure S2. Top-10 rail destinations per gateway, weekday 06:00–09:59 (Jun 2025–Mar 2026)",
                 fontsize=14, fontweight="bold")
    save(fig, "figS2_top10_per_gateway")


def figS3_industrial_rhythms():
    h = io.read_table("rhythms_industrial_hourly").set_index("hour")
    h = h.loc[:, h.sum() > 0]
    fig, ax = plt.subplots(figsize=(12, 5))
    colours = ["#7c3aed", "#db2777", "#0891b2", "#65a30d", "#ea580c"]
    for col, c in zip(h.columns, colours):
        ax.plot(h.index, h[col], lw=2.3, marker="o", ms=3.5, color=c, label=col)
    _hour_axis(ax)
    ax.set_ylabel("Bus trips from Woodlands Checkpoint (46109)")
    ax.set_xlabel("Hour of boarding at 46109 (weekdays, Jun 2025–Mar 2026)")
    ax.legend(fontsize=9.5)
    ax.set_title("Figure S3. Direct bus trips from the checkpoint to industrial-area stops, by hour",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()
    save(fig, "figS3_industrial_rhythms")


def figS4_interview_spacetime():
    prof = spacetime.load_profiles()
    nodes = prof["corridor_km"]
    fig, ax = plt.subplots(figsize=(13, 10))
    ax.set_facecolor("#fafafa")
    for xv in sorted(set(nodes.values())):
        ax.axvline(xv, color="#e2e8f0", lw=0.8, zorder=1)
    for h in range(25):
        ax.axhline(h, color="#e2e8f0", lw=0.6 if h % 2 == 0 else 0.4, zorder=1)
    ax.axvspan(nodes["JB CIQ"], nodes["Woodlands Checkpoint"], color="#ef4444", alpha=0.08, zorder=0)
    for p in prof["profiles"]:
        for s in spacetime.segments(p["waypoints"]):
            ax.plot([nodes[s["from"]], nodes[s["to"]]], [s["t0"], s["t1"]], color=p["colour"], ls=p["style"],
                    lw=3.5 if s["stationary"] else (4.5 if s["minutes"] > 60 else 3.0),
                    alpha=0.9, solid_capstyle="round", zorder=4)
        for name, t in (p["waypoints"][0], p["waypoints"][-1]):
            ax.scatter(nodes[name], t, s=80, color=p["colour"], edgecolors="white", linewidths=1.5, zorder=6)
    for i, (name, x) in enumerate(sorted(nodes.items(), key=lambda kv: kv[1])):
        y = 24.5 if i % 2 == 0 else 25.8  # stagger labels of close nodes
        ax.text(x, y, f"{name}\n({x:.1f} km)", fontsize=8.5, ha="center", va="top", fontweight="bold")
        ax.plot([x, x], [24.0, y - 0.1], color="#475569", lw=1, clip_on=False)
    ax.set_xlim(-2, max(nodes.values()) + 3)
    ax.set_ylim(0, 24)
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks(range(0, 25, 2))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):02d}:00"))
    ax.set_ylabel("Time of day", fontsize=12, fontweight="bold")
    ax.legend(handles=[Line2D([0], [0], color=p["colour"], ls=p["style"], lw=3, label=p["label"])
                       for p in prof["profiles"]], fontsize=10, loc="upper right", framealpha=0.95)
    ax.set_title("Figure S4. Interview-derived space-time lines (stylised profiles)", fontsize=14,
                 fontweight="bold", pad=14)
    fig.tight_layout()
    save(fig, "figS4_interview_spacetime")


ALL = [fig1_sector_dispersal_map, fig2_spacetime_time_poverty, figS1_checkpoint_hourly, figS2_top10_per_gateway,
       figS3_industrial_rhythms, figS4_interview_spacetime]

