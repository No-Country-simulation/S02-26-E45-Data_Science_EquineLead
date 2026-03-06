"""
Monitoring flow — sin Prefect, diseñado para correr en GitHub Actions.

Correr manualmente:
    uv run python src/monitoring/monitoring_flow.py
"""

import json
import os
from datetime import datetime

import config as cfg
from data_loader import load_current_data, load_reference_data
from evidently import BinaryClassification, DataDefinition, Dataset, Report
from evidently.presets import ClassificationPreset, DataDriftPreset, DataSummaryPreset
from slack_alerts import send_slack_alert

os.makedirs(cfg.REPORT_DIR, exist_ok=True)


def load_data() -> tuple:
    ref_df = load_reference_data()
    print(f"✅ Reference data loaded: {len(ref_df)} rows")

    cur_df = load_current_data()
    print(f"✅ Current data loaded: {len(cur_df)} rows")

    return ref_df, cur_df


def build_datasets(ref_df, cur_df) -> tuple:
    def to_evidently(df):
        return Dataset.from_pandas(
            df,
            data_definition=DataDefinition(
                classification=[
                    BinaryClassification(
                        target=cfg.TARGET_COL,
                        prediction_labels=cfg.PREDICTION_COL,
                    )
                ],
                numerical_columns=["price"],
                categorical_columns=["breed", "color"],
            ),
        )

    return to_evidently(ref_df), to_evidently(cur_df)


def run_report(ds_ref, ds_cur) -> tuple[float, str]:
    report = Report(
        metrics=[
            DataDriftPreset(),
            DataSummaryPreset(),
            ClassificationPreset(),
        ]
    )
    result = report.run(reference_data=ds_ref, current_data=ds_cur)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(cfg.REPORT_DIR, f"monitor_report_{timestamp}.html")
    result.save_html(report_path)
    print(f"✅ Report saved: {report_path}")

    report_dict = json.loads(result.json())
    drift_score = 0.0
    for metric in report_dict.get("metrics", []):
        if "DriftedColumnsCount" in metric.get("metric_id", ""):
            drift_score = metric["value"].get("share", 0.0)
            break

    print(f"📊 Drift score: {drift_score:.3f}")
    return drift_score, report_path


def evaluate_drift(drift_score: float, report_path: str):
    flow_name = "monitoring-github-actions"

    if drift_score > cfg.DRIFT_THRESHOLD:
        msg = (
            f"🚨 *Data drift detected!*\n"
            f"Score: `{drift_score:.3f}` > threshold `{cfg.DRIFT_THRESHOLD}`\n"
            f"Report: `{report_path}`\n"
            f"Run: `{os.getenv('GITHUB_RUN_ID', 'local')}`"
        )
        send_slack_alert(msg, state="WARNING", flow_name=flow_name)
        print(f"⚠️  Drift detected: {drift_score:.3f}")
    else:
        msg = (
            f"✅ *No significant drift detected.*\n"
            f"Score: `{drift_score:.3f}` ≤ threshold `{cfg.DRIFT_THRESHOLD}`\n"
            f"Report: `{report_path}`"
        )
        send_slack_alert(msg, state="SUCCESS", flow_name=flow_name)
        print(f"✅ No drift: {drift_score:.3f}")


def main():
    send_slack_alert(
        "🚀 Monitoring started.",
        state="INFO",
        flow_name="monitoring-github-actions",
    )

    try:
        ref_df, cur_df = load_data()
        ds_ref, ds_cur = build_datasets(ref_df, cur_df)
        drift_score, report_path = run_report(ds_ref, ds_cur)
        evaluate_drift(drift_score, report_path)

    except Exception as e:
        send_slack_alert(
            f"❌ Monitoring failed: `{e}`",
            state="FAILURE",
            flow_name="monitoring-github-actions",
        )
        raise


if __name__ == "__main__":
    main()
