#!/usr/bin/env python3
"""Validate that a review report does not overstate unverified findings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


RESULT_CLASSES = {
    "verified_defect",
    "unverified_risk",
    "verified_pass",
    "suggestion",
    "open_question",
}
DEFECT_FIELDS = (
    "changedLocation",
    "causalChain",
    "trigger",
    "expected",
    "actual",
    "impact",
    "evidence",
)
RISK_FIELDS = ("changedLocation", "causalChain", "blocker", "nextVerification")
RUNTIME_EVIDENCE_TYPES = {"screenshot", "network", "console", "trace", "dom"}


def _missing(finding: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [field for field in fields if not finding.get(field)]


def validate(payload: dict[str, Any]) -> list[str]:
    """Return human-readable contract violations without mutating the report."""

    errors: list[str] = []
    if not isinstance(payload.get("scope"), dict):
        errors.append("scope must be an object")
    if not isinstance(payload.get("checks"), list):
        errors.append("checks must be an array")
    findings = payload.get("findings")
    if not isinstance(findings, list):
        return [*errors, "findings must be an array"]

    for index, finding in enumerate(findings):
        prefix = f"findings[{index}]"
        if not isinstance(finding, dict):
            errors.append(f"{prefix} must be an object")
            continue
        result_class = finding.get("class")
        if result_class not in RESULT_CLASSES:
            errors.append(f"{prefix}.class must be one of {sorted(RESULT_CLASSES)}")
            continue
        if result_class == "verified_defect":
            for field in _missing(finding, DEFECT_FIELDS):
                errors.append(f"{prefix}.{field} is required for verified_defect")
            evidence = finding.get("evidence")
            if isinstance(evidence, list) and finding.get("surface") in {"ui", "ux", "figma", "browser"}:
                evidence_types = {
                    item.get("type") for item in evidence if isinstance(item, dict)
                }
                if not evidence_types.intersection(RUNTIME_EVIDENCE_TYPES):
                    errors.append(f"{prefix}.evidence needs runtime or visual evidence")
        elif result_class == "unverified_risk":
            for field in _missing(finding, RISK_FIELDS):
                errors.append(f"{prefix}.{field} is required for unverified_risk")
        elif result_class in {"suggestion", "open_question"} and finding.get("blocking") is True:
            errors.append(f"{prefix} cannot block the review")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Collab Verified Review JSON report")
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(json.dumps({"valid": False, "errors": [str(error)]}, ensure_ascii=False, indent=2))
        return 1
    errors = validate(payload)
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
