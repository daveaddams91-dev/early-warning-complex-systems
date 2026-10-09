
import pandas as pd
from unittest.mock import patch
from src.advancements.phase4_investigation import (
    run_indicator_tensor_experiment,
    test_hypotheses_h1_to_h8
)


@patch('pandas.DataFrame.to_csv')
def test_run_indicator_tensor_experiment(mock_to_csv):
    df = run_indicator_tensor_experiment(n_runs=2, dt_obs=0.05)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty

    expected_cols = [
        'System', 'Transition_Class', 'Indicator', 'Noise_Label', 'Noise_Std',
        'Trajectory_ROC_AUC', 'Trajectory_PR_AUC', 'Mean_Lead_Time'
    ]
    for col in expected_cols:
        assert col in df.columns

    assert len(df) > 0


@patch('pandas.DataFrame.to_csv')
def test_test_hypotheses_h1_to_h8(mock_to_csv):
    df = test_hypotheses_h1_to_h8(n_runs=2, dt_obs=0.05)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty

    expected_cols = [
        'Hypothesis', 'Condition', 'Theoretical_Prediction',
        'Observed_Metric', 'Support_Verdict'
    ]
    for col in expected_cols:
        assert col in df.columns

    assert len(df) > 0

    # We expect some specific hypotheses to be tested
    hypotheses = df['Hypothesis'].unique()
    assert 'H2_Noise_Dilution' in hypotheses
    assert 'H1_Noise_Averaging' in hypotheses
    assert 'H4_Geometric_Mismatch' in hypotheses
    assert 'H6_Estimation_Instability' in hypotheses
    assert 'H8_Information_Limitation' in hypotheses
