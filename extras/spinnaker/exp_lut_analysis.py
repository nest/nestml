#!/usr/bin/env python3
"""
Trade-offs of fixed-point lookup tables (LUTs) for exponential decay propagators.

Entry k of a table holds the decay over k time steps, exp(-k * DT / TAU), as an
integer code c_k, read back as c_k / 2**F, where F is the number of fractional
bits. Because a propagator is only ever needed for k >= 1, the table starts at
k = 1 and never has to hold 1.0. Every stored value is < 1, so all bits of an
entry can be fractional: F equals the number of value bits per entry.

Compared here:
  bits per entry   8, 16 or 32 (and, in the sweep, every width in between)
  rounding         floor or round when turning exact values into codes

A "natural" table ends where further entries stop being useful: once exp()
drops below 1 LSB (floor) or 0.5 LSB (round), the stored code would be 0 anyway.
All errors are measured over one fixed time window that extends past the end
of every table; a lookup beyond the end of a table returns 0.
"""

import csv
import math
import sys
from dataclasses import dataclass
from pathlib import Path

from matplotlib.ticker import ScalarFormatter
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


# shared figure style, kept with the SpiNNaker tests
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests" / "spinnaker_tests"))
from spinnaker_test_utils import apply_publication_style

apply_publication_style()


# ============================================================================
# Configuration
# ============================================================================

DT = 1.0      # simulation time step (ms)
TAU = 20.0    # decay time constant (ms)

# Unsigned storage gives one more value bit (and so one more fractional bit)
# than signed storage of the same width.
SIGNED = False

WORD_SIZES = (8, 16, 32)          # storage widths written to CSV and compared directly
SWEEP_BITS = range(4, 33)         # every width for the bits sweep
FIXED_LENGTHS = (50, 100, 200, 400)   # fixed table lengths shown in the bits sweep
ROUNDINGS = ("floor", "round")

OUTPUT_DIR = Path("lut_output")


# ============================================================================
# Plot style (Okabe-Ito colour-blind safe palette)
# ============================================================================

ROUND_COLORS = {"floor": "#D55E00", "round": "#0072B2"}
ROUND_MARKERS = {"floor": "v", "round": "o"}
LENGTH_CMAP = plt.get_cmap("viridis")

# ============================================================================
# Tables
# ============================================================================

DECAY_PER_STEP = DT / TAU
ROUNDERS = {"floor": np.floor, "round": np.round}


@dataclass
class Table:
    bits: int           # storage bits per entry
    rounding: str
    codes: np.ndarray   # codes[i] holds k = i + 1; value = code / 2**frac_bits

    @property
    def frac_bits(self):
        return frac_bits_for(self.bits)

    @property
    def length(self):
        return len(self.codes)

    @property
    def lsb(self):
        return 2.0 ** -self.frac_bits

    @property
    def memory_bytes(self):
        """Bytes when stored in the smallest 8/16/32-bit container that fits."""
        return self.length * container_bits(self.bits) // 8

    @property
    def packed_bytes(self):
        """Bytes when entries are bit-packed with no padding."""
        return math.ceil(self.length * self.bits / 8)

    @property
    def name(self):
        return f"{self.rounding}_F{self.frac_bits}"


def frac_bits_for(bits):
    return bits - 1 if SIGNED else bits


def container_bits(bits):
    return next(c for c in (8, 16, 32, 64) if c >= bits)


def natural_length(bits, rounding):
    """Entries k = 1..K worth storing (padded to whole 32-bit words for 8/16/32-bit entries).

    An entry is worth storing while its code is non-zero: until exp() drops
    below 1 LSB for floor, or below 0.5 LSB for round.
    """
    threshold_lsb = 1.0 if rounding == "floor" else 0.5
    count = math.floor((frac_bits_for(bits) * math.log(2) - math.log(threshold_lsb))
                       / DECAY_PER_STEP)
    if bits in (8, 16, 32):
        per_word = 32 // bits
        count = -(-count // per_word) * per_word
    return count


def make_table(bits, rounding, length=None):
    if length is None:
        length = natural_length(bits, rounding)
    k = np.arange(1, length + 1)
    scaled = np.exp(-k * DECAY_PER_STEP) * 2.0 ** frac_bits_for(bits)
    max_code = (1 << frac_bits_for(bits)) - 1
    # The clip only matters if exp(-dt/tau) rounds up to 1.0 (very long tau)
    codes = np.clip(ROUNDERS[rounding](scaled), 0, max_code).astype(np.int64)
    return Table(bits, rounding, codes)


# ============================================================================
# Error over a fixed time window
# ============================================================================

def make_window():
    """Time steps k >= 1 until exp() is below half an LSB of the finest table."""
    f_max = max(frac_bits_for(b) for b in list(SWEEP_BITS) + list(WORD_SIZES))
    n_steps = math.ceil((f_max + 2) * math.log(2) / DECAY_PER_STEP)
    n_steps = max(n_steps, max(FIXED_LENGTHS) + 1)
    return np.arange(1, n_steps + 1)


STEPS = make_window()
EXACT = np.exp(-STEPS * DECAY_PER_STEP)


def lookup(table, steps=STEPS):
    """What the simulation reads for each elapsed number of steps (0 past the end)."""
    i = steps - 1
    inside = i < table.length
    out = np.zeros(steps.shape)
    out[inside] = table.codes[i[inside]] * table.lsb
    return out


def errors(table):
    """Signed error per time step; negative means the table decays too fast."""
    return lookup(table) - EXACT


def metrics(table):
    err = errors(table)
    stored = STEPS <= table.length
    return {
        "max_abs_error": float(np.max(np.abs(err))),
        "rms_error": float(np.sqrt(np.mean(err ** 2))),
        # systematic bias of the stored entries, in units of this table's LSB
        "bias_lsb": float(np.mean(err[stored]) / table.lsb),
    }


# ============================================================================
# CSV output
# ============================================================================

def write_table_csvs(tables):
    """One CSV per word size; one column of integer codes per rounding."""
    paths = []
    for bits in WORD_SIZES:
        group = [t for t in tables if t.bits == bits]
        n_rows = max(t.length for t in group)
        path = OUTPUT_DIR / f"lut_{bits}bit.csv"

        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["k", "t_ms", "exact"] + [t.name for t in group])
            for k in range(1, n_rows + 1):
                row = [k, k * DT, f"{math.exp(-k * DECAY_PER_STEP):.12g}"]
                for t in group:
                    row.append(int(t.codes[k - 1]) if k <= t.length else "")
                writer.writerow(row)
        paths.append(path)
    return paths


# ============================================================================
# Figures
# ============================================================================

def plot_anatomy(widths=(11,)):
    """Quantisation and truncation up close, in units of each table's LSB."""
    fig, axes = plt.subplots(2, len(widths), figsize=(6.5 * len(widths) + 1.5, 7.5),
                             squeeze=False, constrained_layout=True)

    for col, bits in enumerate(widths):
        tables = {r: make_table(bits, r) for r in ROUNDINGS}
        lsb = tables["floor"].lsb
        ends = {r: t.length for r, t in tables.items()}

        # zoom on the tail, where values are a dozen LSBs or fewer
        start = int((frac_bits_for(bits) * math.log(2) - math.log(12)) / DECAY_PER_STEP)
        stop = int(1.12 * max(ends.values()))
        zoom = STEPS[(STEPS >= start) & (STEPS <= stop)]

        ax = axes[0, col]
        t_fine = np.linspace(zoom[0], zoom[-1], 800)
        ax.plot(t_fine, np.exp(-t_fine * DECAY_PER_STEP) / lsb, color="black",
                label="exact exp(−t/τ)", zorder=1)
        for r in ROUNDINGS:
            ax.plot(zoom, lookup(tables[r], zoom) / lsb, ls="none",
                    marker=ROUND_MARKERS[r],
                    color=ROUND_COLORS[r], label=r)
        ax.set_title(f"{bits}-bit entries (F = {frac_bits_for(bits)}): tail of the table")
        ax.set_ylabel("value (LSBs)")
        ax.set_xlabel("time steps k")

        ax = axes[1, col]
        span = STEPS[STEPS <= int(1.3 * max(ends.values()))]
        for r in ROUNDINGS:
            ax.plot(span, errors(tables[r])[: len(span)] / lsb, ls="none",
                    marker=ROUND_MARKERS[r],
                    color=ROUND_COLORS[r], label=r)
        for y in (-1, -0.5, 0, 0.5):
            ax.axhline(y, color="black", alpha=0.4, zorder=0)
        ax.set_title(f"{bits}-bit entries: error over the window")
        ax.set_ylabel("lookup − exact (LSBs)")
        ax.set_xlabel("time steps k")
        sec = ax.secondary_yaxis("right", functions=(lambda y, l=lsb: y * l,
                                                      lambda y, l=lsb: y / l))
        sec.set_ylabel("lookup − exact (absolute)")
        fmt = ScalarFormatter(useMathText=True)
        fmt.set_powerlimits((0, 0))      # always factor out the exponent
        sec.yaxis.set_major_formatter(fmt)

        for row, ax in enumerate(axes[:, col]):
            for r in ROUNDINGS:
                ax.axvline(ends[r], color=ROUND_COLORS[r], ls=":")
                if row == 0:   # label once; the error panel is too busy
                    ax.text(ends[r], 0.98, f" {r} end ({ends[r]})", color=ROUND_COLORS[r],
                            va="top", ha="right", rotation=90,
                            transform=ax.get_xaxis_transform())

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=3)
    # fig.suptitle(f"Exponential-decay LUT up close  (τ = {TAU:g} ms, dt = {DT:g} ms, "
    #              f"table starts at k = 1)", fontsize=13, fontweight="bold")
    return fig

def plot_bits_tradeoff(roundings=("round", "floor")):
    """Error and table length against bits per entry, for natural-length tables."""
    fig, (ax_err, ax_len) = plt.subplots(2, 1, figsize=(8, 5), sharex=True,
                                         constrained_layout=True,
                                         gridspec_kw={"height_ratios": [1, 1]})
    bits = np.array(list(SWEEP_BITS))
    metric_styles = {"max_abs_error": ("-", "o", "max |error|"),
                     "rms_error": ("--", "s", "RMS error")}

    for rounding in roundings:
        tables = [make_table(b, rounding) for b in bits]
        table_metrics = [metrics(t) for t in tables]
        color = ROUND_COLORS[rounding]

        for key, (ls, marker, _) in metric_styles.items():
            ax_err.plot(bits, [m[key] for m in table_metrics], ls=ls, marker=marker,
                        color=color)

        lengths = [t.length for t in tables]
        ax_len.plot(bits, lengths, marker=ROUND_MARKERS[rounding],
                    color=color)

    ax_err.set_yscale("log")
    ax_err.set_ylabel("error over window")
    ax_len.set_ylabel("table length (words)")
    ax_len.set_xticks([4, 8, 12, 16, 20, 24, 28, 32])
    ax_len.set_xlabel("bits per entry (= fractional bits)" if not SIGNED
                      else "bits per entry (fractional bits = bits − 1)")

    handles = (
        [Line2D([], [], color=ROUND_COLORS[r], label=r) for r in roundings]
        + [Line2D([], [], color="grey", ls=ls, marker=m, label=label)
           for ls, m, label in metric_styles.values()]
    )
    ax_err.legend(handles=handles, loc="upper right", ncol=2)
    # fig.suptitle("Natural-length tables: accuracy and size vs bits per entry", fontsize=12, fontweight="bold")
    return fig

def plot_natural_summary(tables):
    """Rounding comparison for the natural-length 8/16/32-bit tables."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5), sharex=True, constrained_layout=True)
    x = np.arange(len(WORD_SIZES))
    width = 0.36
    by_key = {(t.bits, t.rounding): t for t in tables}

    panels = [
        ("max_abs_error", "max |error| over window", "Worst case", True),
        ("rms_error", "RMS error over window", "Typical", True),
        ("bias_lsb", "mean error of stored entries (LSBs)",
         "Systematic bias (− means the table decays too fast)", False),
        ("memory", "table memory (bytes)", "Cost", True),
    ]

    for ax, (key, ylabel, title, log) in zip(axes.flat, panels):
        for j, rounding in enumerate(ROUNDINGS):
            ts = [by_key[(b, rounding)] for b in WORD_SIZES]
            vals = [t.memory_bytes if key == "memory" else metrics(t)[key] for t in ts]
            bars = ax.bar(x + (j - 0.5) * width, vals, width, color=ROUND_COLORS[rounding],
                          label=rounding, edgecolor="white", linewidth=0.5)
            if key == "memory":
                ax.bar_label(bars, fontsize=8, padding=2)
        if log:
            ax.set_yscale("log")
        else:
            ax.axhline(0, color="black")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(axis="x", visible=False)

    for ax in axes[1]:
        ax.set_xticks(x)
        ax.set_xticklabels([f"{b}-bit\nF = {frac_bits_for(b)}" for b in WORD_SIZES])
    axes[0, 0].legend(title="rounding", loc="upper right")
    # fig.suptitle("Natural-length tables: floor vs round", fontsize=13, fontweight="bold")
    return fig


# ============================================================================
# Main
# ============================================================================

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tables = [make_table(b, r) for b in WORD_SIZES for r in ROUNDINGS]

    print(f"tau = {TAU:g} ms, dt = {DT:g} ms, {'signed' if SIGNED else 'unsigned'}, "
          f"table starts at k = 1")
    print(f"error window: k = 1..{STEPS[-1]}\n")
    header = f"{'table':<20}{'entries':>8}{'bytes':>7}{'max|err|':>12}{'rms':>12}{'bias/LSB':>10}"
    print(header)
    print("-" * len(header))
    for t in tables:
        m = metrics(t)
        print(f"{f'{t.bits}-bit {t.name}':<20}{t.length:>8}{t.memory_bytes:>7}"
              f"{m['max_abs_error']:>12.3e}{m['rms_error']:>12.3e}{m['bias_lsb']:>10.3f}")

    csv_paths = write_table_csvs(tables)

    figures = {
        "exp_lut_error_distribution.png": plot_anatomy(),
        "exp_lut_accuracy_size_vs_bits.png": plot_bits_tradeoff(),
        # "3_natural_length_summary.png": plot_natural_summary(tables),
    }
    for filename, fig in figures.items():
        fig.savefig(OUTPUT_DIR / filename)
        plt.close(fig)

    print(f"\nwrote to {OUTPUT_DIR.resolve()}:")
    for p in csv_paths:
        print(f"  {p.name}")
    for filename in figures:
        print(f"  {filename}")


if __name__ == "__main__":
    main()
