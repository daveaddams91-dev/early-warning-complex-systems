'''Automated Research Reporting Script.

Ingests raw validated CSV results from ``results/validated/tables/`` and
generates reproducible Markdown tables and figures for documentation.
'''

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

__all__ = ["df_to_markdown", "generate_all_reports"]


def _format_value(value: object) -> str:
    """Return a string representation suitable for a markdown table.

    Floats (including ``numpy`` floating types) are formatted with four
    decimal places; everything else is converted with ``str``.
    """
    if isinstance(value, (float, np.floating)):
        # ``:.4f`` works for ``np.float64`` as well.
        return f"{value:.4f}"
    return str(value)


def df_to_markdown(df: pd.DataFrame, include_index: bool = True) -> str:
    """Convert a :class:`pandas.DataFrame` to a GitHub‑flavoured markdown table.

    Parameters
    ----------
    df:
        DataFrame to render.
    include_index:
        If ``True`` the index is reset and rendered as the first column;
        otherwise the index is omitted.

    Returns
    -------
    str
        Markdown representation of *df*.
    """
    df_render: pd.DataFrame = df.reset_index() if include_index else df.copy()
    headers: List[str] = [str(col) for col in df_render.columns]

    lines: List[str] = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    for _, row in df_render.iterrows():
        formatted = [_format_value(v) for v in row]
        lines.append("| " + " | ".join(formatted) + " |")

    return "\n".join(lines)


def _print_header(title: str) -> None:
    """Print a markdown header surrounded by a visual separator."""
    separator = "=" * 70
    print(separator)
    print(title)
    print(separator)


def generate_all_reports(tables_dir: Path | str = Path("results/validated/tables")) -> None:
    """Generate all markdown tables used in the research report.

    The function reads a predefined set of CSV files located in *tables_dir*,
    converts the relevant slices to markdown and prints them to ``stdout``.
    It is deliberately side‑effect free apart from the printing, which mirrors
    the original script's behaviour.

    Parameters
    ----------
    tables_dir:
        Directory that contains the validated CSV tables.  The default matches
        the historic location used by the repository.
    """
    tables_path = Path(tables_dir)

    if not tables_path.is_dir():
        print("Validated tables directory not found.", file=sys.stderr)
        return

    # Mapping of CSV filenames to the callable that renders the corresponding table.
    csv_map = {
        "validated_clean_benchmark.csv": _render_clean_benchmark,
        "validated_clustered_bootstrap_significance.csv": _render_bootstrap_significance,
        "validated_stress_and_corruption_benchmark.csv": _render_stress_corruption,
        "validated_unknown_transition_generalization.csv": _render_unknown_transition,
    }

    for filename, renderer in csv_map.items():
        csv_path = tables_path / filename
        if csv_path.is_file():
            try:
                df = pd.read_csv(csv_path)
            except Exception as exc:  # pragma: no cover – defensive programming
                print(f"Failed to read {csv_path}: {exc}", file=sys.stderr)
                continue
            renderer(df)


def _render_clean_benchmark(df: pd.DataFrame) -> None:
    _print_header("GENERATING AUTOMATED RESEARCH SUMMARY TABLES")
    print("\n### Table 1: Validated Clean Benchmark (Trajectory-Level ROC‑AUC)")
    piv = df.pivot(index="System", columns="Method", values="Trajectory_ROC_AUC")
    desired = [
        "Variance",
        "AR(1)",
        "PermutationEntropy",
        "CEWF-Rank",
        "CEWF-Mahalanobis",
        "Adaptive-Bayesian-EWS",
    ]
    selected = [c for c in desired if c in piv.columns]
    if selected:
        print(df_to_markdown(piv[selected], include_index=True))
    else:
        print("No matching columns found for clean benchmark.", file=sys.stderr)


def _render_bootstrap_significance(df: pd.DataFrame) -> None:
    print("\n### Table 2: Clustered Realization Bootstrap Significance (Delta AUC vs AR(1))")
    cols = [
        "System",
        "Comparison",
        "Delta_AUC_Mean",
        "CI_Lower_95",
        "CI_Upper_95",
        "Bootstrap_p_value",
        "Significant_at_005",
    ]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        print(f"Missing columns in bootstrap CSV: {missing}", file=sys.stderr)
        return
    print(df_to_markdown(df[cols], include_index=False))


def _render_stress_corruption(df: pd.DataFrame) -> None:
    print("\n### Table 3: Stress and Corruption Robustness (Trajectory-Level ROC‑AUC on May Fold)")
    piv = df.pivot(index="Scenario", columns="Method", values="Trajectory_ROC_AUC")
    desired = [
        "Variance",
        "AR(1)",
        "PermutationEntropy",
        "CEWF-Rank",
        "CEWF-Mahalanobis",
        "Adaptive-Bayesian-EWS",
    ]
    selected = [c for c in desired if c in piv.columns]
    if selected:
        print(df_to_markdown(piv[selected], include_index=True))
    else:
        print("No matching columns found for stress/corruption table.", file=sys.stderr)


def _render_unknown_transition(df: pd.DataFrame) -> None:
    print("\n### Table 4: Unknown‑Transition Zero‑Knowledge Generalization (Adler SNIC)")
    cols = [
        "System",
        "Transition_Mechanism",
        "Method",
        "Trajectory_ROC_AUC",
        "True_Positive_Rate",
        "Mean_Lead_Time",
        "Zero_Knowledge_Generalization",
    ]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        print(f"Missing columns in unknown‑transition CSV: {missing}", file=sys.stderr)
        return
    print(df_to_markdown(df[cols], include_index=False))


if __name__ == "__main__":
    generate_all_reports()
