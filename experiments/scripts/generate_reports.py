"""
Automated Research Reporting Script.
Ingests raw validated CSV results from results/validated/tables/
and generates reproducible Markdown tables and figures for documentation.
"""

from pathlib import Path
import numpy as np
import pandas as pd


def df_to_markdown(df: pd.DataFrame, include_index: bool = True) -> str:
    """Converts a pandas DataFrame to a GitHub Markdown table without external dependencies."""
    if include_index:
        df_reset = df.reset_index()
    else:
        df_reset = df.copy()
    headers = [str(c) for c in df_reset.columns]
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in df_reset.iterrows():
        row_str = [f"{val:.4f}" if isinstance(val, (float, np.floating)) else str(val) for val in row]
        lines.append("| " + " | ".join(row_str) + " |")
    return "\n".join(lines)


def generate_all_reports():
    tables_dir = Path("results/validated/tables")
    if not tables_dir.exists():
        print("Validated tables directory not found.")
        return

    clean_csv = tables_dir / "validated_clean_benchmark.csv"
    boot_csv = tables_dir / "validated_clustered_bootstrap_significance.csv"
    corrupt_csv = tables_dir / "validated_stress_and_corruption_benchmark.csv"
    snic_csv = tables_dir / "validated_unknown_transition_generalization.csv"

    print("=" * 70)
    print("GENERATING AUTOMATED RESEARCH SUMMARY TABLES")
    print("=" * 70)

    # 1. Clean Benchmark Summary Table
    if clean_csv.exists():
        df_clean = pd.read_csv(clean_csv)
        print("\n### Table 1: Validated Clean Benchmark (Trajectory-Level ROC-AUC)")
        piv = df_clean.pivot(index='System', columns='Method', values='Trajectory_ROC_AUC')
        selected_cols = [c for c in ['Variance', 'AR(1)', 'PermutationEntropy', 'CEWF-Rank', 'CEWF-Mahalanobis', 'Adaptive-Bayesian-EWS'] if c in piv.columns]
        print(df_to_markdown(piv[selected_cols], include_index=True))

    # 2. Clustered Bootstrap Significance Table
    if boot_csv.exists():
        df_boot = pd.read_csv(boot_csv)
        print("\n### Table 2: Clustered Realization Bootstrap Significance (Delta AUC vs AR(1))")
        df_boot_disp = df_boot[['System', 'Comparison', 'Delta_AUC_Mean', 'CI_Lower_95', 'CI_Upper_95', 'Bootstrap_p_value', 'Significant_at_005']]
        print(df_to_markdown(df_boot_disp, include_index=False))

    # 3. Stress & Corruption Robustness Table
    if corrupt_csv.exists():
        df_corrupt = pd.read_csv(corrupt_csv)
        print("\n### Table 3: Stress and Corruption Robustness (Trajectory-Level ROC-AUC on May Fold)")
        piv_corrupt = df_corrupt.pivot(index='Scenario', columns='Method', values='Trajectory_ROC_AUC')
        selected_cols_c = [c for c in ['Variance', 'AR(1)', 'PermutationEntropy', 'CEWF-Rank', 'CEWF-Mahalanobis', 'Adaptive-Bayesian-EWS'] if c in piv_corrupt.columns]
        print(df_to_markdown(piv_corrupt[selected_cols_c], include_index=True))

    # 4. Unknown Transition Generalization Table
    if snic_csv.exists():
        df_snic = pd.read_csv(snic_csv)
        print("\n### Table 4: Unknown-Transition Zero-Knowledge Generalization (Adler SNIC)")
        df_snic_disp = df_snic[['System', 'Transition_Mechanism', 'Method', 'Trajectory_ROC_AUC', 'True_Positive_Rate', 'Mean_Lead_Time', 'Zero_Knowledge_Generalization']]
        print(df_to_markdown(df_snic_disp, include_index=False))


if __name__ == "__main__":
    generate_all_reports()
