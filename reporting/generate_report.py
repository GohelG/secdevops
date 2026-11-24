#!/usr/bin/env python3
"""Summarize a Trivy JSON report and optionally send a Slack notification."""
import json
import os
import sys
import urllib.request
from collections import Counter
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 reporting/generate_report.py <path_to_scan_report.json>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(report, dict) or not isinstance(report.get("Results"), list):
            raise ValueError("Invalid Trivy JSON report: missing Results array")
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    image = report.get("ArtifactName") or path.stem
    counts = Counter()
    for result in report["Results"]:
        for vuln in result.get("Vulnerabilities") or []:
            counts[str(vuln.get("Severity", "UNKNOWN")).upper()] += 1

    print(f"Image: {image}")
    print("Vulnerabilities: " + ", ".join(
        f"{severity}={counts[severity]}"
        for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN")
    ))

    webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook:
        print("SLACK_WEBHOOK_URL is not configured; notification skipped.")
        return 0

    message = {
        "text": (
            f"Trivy scan: {image}\n"
            f"HIGH: {counts['HIGH']} | CRITICAL: {counts['CRITICAL']}\n"
            f"Report: {path.name}"
        )
    }
    request = urllib.request.Request(
        webhook,
        data=json.dumps(message).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            print(f"Slack notification HTTP {response.status}")
    except Exception as exc:
        print(f"ERROR: Slack notification failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
