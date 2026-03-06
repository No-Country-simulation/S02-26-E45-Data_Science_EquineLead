from datetime import datetime

import config as cfg
import requests


def send_slack_alert(message: str, state: str, flow_name: str):
    """
    Envía una alerta a Slack con formato estructurado.

    Args:
        message: Cuerpo del mensaje
        state:   SUCCESS | FAILURE | WARNING | INFO
        flow_name: Nombre del flow de Prefect
    """
    color = {
        "SUCCESS": "#36a64f",
        "FAILURE": "#ff0000",
        "INFO": "#3AA3E3",
        "WARNING": "#FFA500",
    }.get(state, "#cccccc")

    emoji = {
        "SUCCESS": "✅",
        "FAILURE": "❌",
        "INFO": "ℹ️",
        "WARNING": "⚠️",
    }.get(state, "ℹ️")

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    template = {
        "attachments": [
            {
                "color": color,
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{emoji} EquineLead Monitor — {state}",
                            "emoji": True,
                        },
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*Flow:* `{flow_name}`"},
                            {"type": "mrkdwn", "text": f"*Status:* *{state}*"},
                            {"type": "mrkdwn", "text": f"*Time:* {date}"},
                        ],
                    },
                ],
            }
        ]
    }

    if message:
        template["attachments"][0]["blocks"].append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Message:* {message}"},
            }
        )

    if not cfg.SLACK_WEBHOOK_URL:
        print("⚠️  SLACK_WEBHOOK_URL not configured — skipping alert.")
        return

    response = requests.post(cfg.SLACK_WEBHOOK_URL, json=template)
    if response.status_code == 200:
        print("✅ Slack alert sent.")
    else:
        print(f"❌ Slack alert failed: {response.status_code} {response.text}")
