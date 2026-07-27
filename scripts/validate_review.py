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
REACHABILITY_RESULTS = {"ready", "probe", "blocked", "not_applicable"}
PROJECT_KNOWLEDGE_STATUSES = {"used", "unavailable", "not_applicable"}
PROJECT_KNOWLEDGE_MODES = {"requirement_review", "recall"}
HISTORICAL_COMPATIBILITY = {"verified", "conflict", "unverified", "not_applicable"}


def _missing(finding: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [field for field in fields if not finding.get(field)]


def validate(payload: dict[str, Any]) -> list[str]:
    """Return human-readable contract violations without mutating the report."""

    errors: list[str] = []
    if not isinstance(payload.get("scope"), dict):
        errors.append("scope must be an object")
    project_knowledge = payload.get("projectKnowledge")
    if not isinstance(project_knowledge, dict):
        errors.append("projectKnowledge must be an object")
    else:
        prefix = "projectKnowledge"
        if project_knowledge.get("provider") != "know-all-agent":
            errors.append(f"{prefix}.provider must be know-all-agent")
        status = project_knowledge.get("status")
        if status not in PROJECT_KNOWLEDGE_STATUSES:
            errors.append(
                f"{prefix}.status must be one of {sorted(PROJECT_KNOWLEDGE_STATUSES)}"
            )
        compatibility = project_knowledge.get("historicalCompatibility")
        if compatibility not in HISTORICAL_COMPATIBILITY:
            errors.append(
                f"{prefix}.historicalCompatibility must be one of "
                f"{sorted(HISTORICAL_COMPATIBILITY)}"
            )
        if status == "used":
            mode = project_knowledge.get("mode")
            if mode not in PROJECT_KNOWLEDGE_MODES:
                errors.append(
                    f"{prefix}.mode must be one of {sorted(PROJECT_KNOWLEDGE_MODES)}"
                )
            for field in (
                "projectId",
                "projectRevision",
                "reviewedRevision",
                "currentRules",
                "supersededRules",
                "sources",
                "unresolved",
            ):
                if project_knowledge.get(field) in (None, ""):
                    errors.append(f"{prefix}.{field} is required when status is used")
            for field in ("currentRules", "supersededRules", "sources", "unresolved"):
                if field in project_knowledge and not isinstance(
                    project_knowledge.get(field), list
                ):
                    errors.append(f"{prefix}.{field} must be an array")
            if mode == "requirement_review" and not project_knowledge.get("taskId"):
                errors.append(
                    f"{prefix}.taskId is required for requirement_review mode"
                )
            if (
                project_knowledge.get("projectRevision")
                and project_knowledge.get("reviewedRevision")
                and project_knowledge["projectRevision"]
                != project_knowledge["reviewedRevision"]
            ):
                errors.append(
                    f"{prefix}.projectRevision must match reviewedRevision"
                )
            if compatibility in {"verified", "conflict"} and not project_knowledge.get(
                "sources"
            ):
                errors.append(
                    f"{prefix}.sources is required when historical compatibility "
                    f"is {compatibility}"
                )
        elif status == "unavailable":
            if not project_knowledge.get("reason"):
                errors.append(f"{prefix}.reason is required when status is unavailable")
            if compatibility != "unverified":
                errors.append(
                    f"{prefix}.historicalCompatibility must be unverified when "
                    "status is unavailable"
                )
        elif status == "not_applicable":
            if not project_knowledge.get("reason"):
                errors.append(
                    f"{prefix}.reason is required when status is not_applicable"
                )
            if compatibility != "not_applicable":
                errors.append(
                    f"{prefix}.historicalCompatibility must be not_applicable when "
                    "status is not_applicable"
                )
    checks = payload.get("checks")
    if not isinstance(checks, list):
        errors.append("checks must be an array")
    else:
        for index, check in enumerate(checks):
            prefix = f"checks[{index}]"
            if not isinstance(check, dict):
                errors.append(f"{prefix} must be an object")
                continue
            if check.get("type") != "browser":
                continue
            plan = check.get("reachabilityPlan")
            if not isinstance(plan, dict):
                errors.append(f"{prefix}.reachabilityPlan is required for browser checks")
                continue
            if not plan.get("hypothesis"):
                errors.append(f"{prefix}.reachabilityPlan.hypothesis is required")
            readiness = plan.get("readiness")
            if readiness not in REACHABILITY_RESULTS:
                errors.append(
                    f"{prefix}.reachabilityPlan.readiness must be one of {sorted(REACHABILITY_RESULTS)}"
                )
            if not plan.get("target"):
                errors.append(f"{prefix}.reachabilityPlan.target is required")
            browser_plan = plan.get("browserPlan")
            if readiness in {"ready", "probe"}:
                if not isinstance(browser_plan, dict):
                    errors.append(f"{prefix}.reachabilityPlan.browserPlan is required for {readiness}")
                else:
                    for field in ("url", "expected", "stopConditions"):
                        if browser_plan.get(field) in (None, "", []):
                            errors.append(f"{prefix}.reachabilityPlan.browserPlan.{field} is required")
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
