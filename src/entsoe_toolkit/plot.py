import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from entsoe_toolkit import io


def clean_label(label):
    label = re.sub(r"\s+", " ", str(label)).strip()
    return label.replace("_", " ").title()


def plot_generation_shares(area_name, shares):
    percentages = shares.fillna(0) * 100
    percentages.index = pd.to_datetime(percentages.index)

    columns = [col for col in percentages.columns if col != "Other"]
    if "Other" in percentages.columns:
        columns.append("Other")
    percentages = percentages[columns]

    plot_data = percentages.copy()
    plot_data.index = range(len(plot_data))

    tab20 = plt.get_cmap("tab20")
    colors = [tab20(i % tab20.N) for i in range(len(columns))]
    if columns and columns[-1] == "Other":
        colors[-1] = "#b8b8b8"

    ax = plot_data.plot.area(
        figsize=(13, 7),
        stacked=True,
        linewidth=0,
        alpha=0.95,
        color=colors,
    )

    ax.set_title(f"{area_name}: monthly electricity generation mix")
    ax.set_xlabel("Month")
    ax.set_ylabel("Share of monthly generation (%)")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.0f}%")

    if len(percentages) > 0:
        tick_positions = list(range(0, len(percentages), 6))
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(
            [percentages.index[position].strftime("%b %Y") for position in tick_positions],
            rotation=35,
            ha="right",
        )
        ax.set_xlim(0, len(percentages) - 1)
        ax.margins(x=0)

    ax.grid(True, axis="y", alpha=0.3)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles,
        [clean_label(label) for label in labels],
        title="Production type",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.14),
        ncol=3,
        frameon=False,
    )

    plt.tight_layout()
    path = io.plot_path(area_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    return path

