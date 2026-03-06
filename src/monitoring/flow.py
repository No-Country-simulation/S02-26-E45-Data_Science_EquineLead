import json
import os
from datetime import datetime

import config as cfg
from data_loader import load_current_data, load_reference_data
from evidently.metric_preset import (
    ClassificationPreset,
    DataDriftPreset,
    DataQualityPreset,
    TargetDriftPreset,
)
from evidently.metrics import (
    ClassificationClassBalance,
    ClassificationConfusionMatrix,
    ClassificationQualityByClass,
    ClassificationQualityMetric,
    ColumnDistributionMetric,
    ColumnDriftMetric,
    DataDriftTable,
    DatasetDriftMetric,
    DatasetMissingValuesMetric,
)
from evidently.pipeline.column_mapping import ColumnMapping
from evidently.report import Report
from netlify_deploy import deploy_report
from slack_alerts import send_slack_alert

os.makedirs(cfg.REPORT_DIR, exist_ok=True)

NUMERICAL_COLS = [
    "horses_viewed",
    "horses_added_to_cart",
    "max_horse_price_viewed",
    "viewed_premium_horses",
    "viewed_sport_elite",
    "caballos_unicos_vistos",
    "ratio_recurrencia_horse",
    "ratio_cart_horse",
    "user_prestige_score",
    "user_antiguedad_dias",
    "user_region",
    "user_card_issuer",
    "user_domain",
    "prob_plata_oro",
    "prob_oro",
]

KEY_FEATURES = [
    "max_horse_price_viewed",
    "ratio_cart_horse",
    "viewed_premium_horses",
    "horses_viewed",
    "user_prestige_score",
    "prob_plata_oro",
    "prob_oro",
]


def build_column_mapping(ref_df) -> ColumnMapping:
    num_cols = [c for c in NUMERICAL_COLS if c in ref_df.columns]
    return ColumnMapping(
        target=cfg.TARGET_COL,
        prediction=cfg.PREDICTION_COL,
        numerical_features=num_cols,
    )


def load_data():
    ref_df = load_reference_data()
    print(f"✅ Reference: {len(ref_df)} filas")
    cur_df = load_current_data()
    print(f"✅ Current:   {len(cur_df)} filas")
    return ref_df, cur_df


def run_report(ref_df, cur_df) -> tuple[float, str]:
    column_mapping = build_column_mapping(ref_df)

    key_drift_metrics = [
        ColumnDriftMetric(column_name=col)
        for col in KEY_FEATURES
        if col in ref_df.columns
    ]
    key_dist_metrics = [
        ColumnDistributionMetric(column_name=col)
        for col in ["max_horse_price_viewed", "prob_plata_oro", "prob_oro"]
        if col in ref_df.columns
    ]

    report = Report(
        metrics=[
            DataDriftPreset(),
            TargetDriftPreset(),
            DatasetDriftMetric(),
            DataDriftTable(),
            *key_drift_metrics,
            DataQualityPreset(),
            DatasetMissingValuesMetric(),
            ClassificationPreset(),
            ClassificationQualityMetric(),
            ClassificationQualityByClass(),
            ClassificationConfusionMatrix(),
            ClassificationClassBalance(),
            *key_dist_metrics,
        ]
    )

    report.run(
        reference_data=ref_df,
        current_data=cur_df,
        column_mapping=column_mapping,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(cfg.REPORT_DIR, f"horse_monitor_{timestamp}.html")
    report.save_html(report_path)
    print(f"✅ Reporte guardado: {report_path}")

    report_dict = json.loads(report.json())
    drift_score = 0.0
    for metric in report_dict.get("metrics", []):
        if metric.get("metric") == "DatasetDriftMetric":
            drift_score = metric.get("result", {}).get("share_of_drifted_columns", 0.0)
            break

    print(f"📊 Drift score: {drift_score:.3f}")
    return drift_score, report_path


def evaluate_drift(drift_score: float, report_path: str):
    flow_name = "horse-monitoring-github-actions"

    # Subir reporte a Netlify
    try:
        public_url = deploy_report(report_path)
    except Exception as e:
        print(f"⚠️  Netlify deploy falló: {e}")
        public_url = report_path  # fallback al path local

    if drift_score > cfg.DRIFT_THRESHOLD:
        msg = (
            f"🚨 *Data drift detectado en modelos HORSE!*\n"
            f"Score: `{drift_score:.3f}` > umbral `{cfg.DRIFT_THRESHOLD}`\n"
            f"Reporte: {public_url}\n"
            f"Run GH: `{os.getenv('GITHUB_RUN_ID', 'local')}`"
        )
        send_slack_alert(msg, state="WARNING", flow_name=flow_name)
    else:
        msg = (
            f"✅ *Sin drift significativo en modelos HORSE.*\n"
            f"Score: `{drift_score:.3f}` ≤ umbral `{cfg.DRIFT_THRESHOLD}`\n"
            f"Reporte: {public_url}"
        )
        send_slack_alert(msg, state="SUCCESS", flow_name=flow_name)


def main():
    send_slack_alert(
        "🚀 Monitoreo HORSE iniciado.",
        state="INFO",
        flow_name="horse-monitoring-github-actions",
    )
    try:
        ref_df, cur_df = load_data()
        drift_score, report_path = run_report(ref_df, cur_df)
        evaluate_drift(drift_score, report_path)
    except Exception as e:
        send_slack_alert(
            f"❌ Monitoreo HORSE falló: `{e}`",
            state="FAILURE",
            flow_name="horse-monitoring-github-actions",
        )
        raise


if __name__ == "__main__":
    main()
