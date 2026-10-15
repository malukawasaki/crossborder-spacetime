"""Shared visual identity and export."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .. import config  # noqa: E402

RC = {
    "figure.facecolor": "white", "axes.facecolor": "white", "axes.edgecolor": "#94a3b8",
    "axes.labelcolor": "#0f172a", "xtick.color": "#334155", "ytick.color": "#334155",
    "text.color": "#0f172a", "grid.color": "#e2e8f0", "grid.linewidth": 0.6,
    "font.family": "sans-serif", "savefig.facecolor": "white",
}
plt.rcParams.update(RC)


def save(fig, name: str, dpi: int = 200) -> None:
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        path = config.FIGURES_DIR / f"{name}.{ext}"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
    print(f"  wrote results/figures/{name}.png/.pdf")
    plt.close(fig)
