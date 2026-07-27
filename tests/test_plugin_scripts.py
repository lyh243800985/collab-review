from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_portability
import package_plugin
import validate_review


class PluginScriptsTest(unittest.TestCase):
    @staticmethod
    def project_knowledge(**overrides):
        payload = {
            "provider": "know-all-agent",
            "status": "used",
            "mode": "recall",
            "projectId": "auto-ops",
            "projectRevision": "abc1234",
            "reviewedRevision": "abc1234",
            "historicalCompatibility": "verified",
            "currentRules": [],
            "supersededRules": [],
            "sources": ["knowledge/projects/auto-ops/events/example.json"],
            "unresolved": [],
        }
        payload.update(overrides)
        return payload

    def test_example_review_passes_evidence_gate(self):
        payload = json.loads((ROOT / "assets" / "example-review.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_review.validate(payload), [])

    def test_verified_defect_requires_attribution_and_evidence(self):
        payload = {
            "scope": {},
            "projectKnowledge": self.project_knowledge(),
            "checks": [],
            "findings": [{"class": "verified_defect", "surface": "ui"}],
        }
        errors = validate_review.validate(payload)
        self.assertTrue(any("changedLocation" in error for error in errors))
        self.assertTrue(any("evidence" in error for error in errors))

    def test_browser_check_requires_reachability_plan(self):
        payload = {
            "scope": {},
            "projectKnowledge": self.project_knowledge(),
            "checks": [{"type": "browser", "result": "blocked"}],
            "findings": [],
        }
        errors = validate_review.validate(payload)
        self.assertIn("checks[0].reachabilityPlan is required for browser checks", errors)

    def test_ready_browser_check_requires_executable_plan(self):
        payload = {
            "scope": {},
            "projectKnowledge": self.project_knowledge(),
            "checks": [
                {
                    "type": "browser",
                    "result": "passed",
                    "reachabilityPlan": {
                        "hypothesis": "R-01",
                        "readiness": "ready",
                        "target": "Sync button",
                        "browserPlan": {
                            "url": "http://test.example/#/detail/1",
                            "expected": "The button is visible",
                            "stopConditions": ["runtime flag is false"],
                        },
                    },
                }
            ],
            "findings": [],
        }
        self.assertEqual(validate_review.validate(payload), [])

    def test_project_knowledge_is_required(self):
        payload = {"scope": {}, "checks": [], "findings": []}
        self.assertIn(
            "projectKnowledge must be an object",
            validate_review.validate(payload),
        )

    def test_unavailable_project_knowledge_keeps_history_unverified(self):
        payload = {
            "scope": {},
            "projectKnowledge": self.project_knowledge(
                status="unavailable",
                historicalCompatibility="unverified",
                reason="Know All Agent is not installed",
            ),
            "checks": [],
            "findings": [],
        }
        self.assertEqual(validate_review.validate(payload), [])

    def test_requirement_review_requires_task_id(self):
        payload = {
            "scope": {},
            "projectKnowledge": self.project_knowledge(mode="requirement_review"),
            "checks": [],
            "findings": [],
        }
        self.assertIn(
            "projectKnowledge.taskId is required for requirement_review mode",
            validate_review.validate(payload),
        )

    def test_project_knowledge_revision_must_match_review(self):
        payload = {
            "scope": {},
            "projectKnowledge": self.project_knowledge(
                projectRevision="old-revision"
            ),
            "checks": [],
            "findings": [],
        }
        self.assertIn(
            "projectKnowledge.projectRevision must match reviewedRevision",
            validate_review.validate(payload),
        )

    def test_distributable_files_are_portable(self):
        self.assertEqual(check_portability.scan(ROOT), [])

    def test_cteam_scripts_are_valid_node_programs(self):
        for name in ("fetch_issue.js", "fetch_issue_image.js"):
            result = subprocess.run(
                ["node", "--check", str(ROOT / "skills" / "collab-verified-review" / "scripts" / name)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_release_contains_orchestrator_and_specialist_skills(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "plugin.zip"
            package_plugin.package(output)
            with zipfile.ZipFile(output) as archive:
                members = set(archive.namelist())
            skill_files = {name for name in members if name.endswith("/SKILL.md")}
            self.assertEqual(
                skill_files,
                {
                    "collab-verified-review/skills/collab-verified-review/SKILL.md",
                    "collab-verified-review/skills/collab-review-context/SKILL.md",
                    "collab-verified-review/skills/collab-review-hypothesis/SKILL.md",
                    "collab-verified-review/skills/collab-review-reachability/SKILL.md",
                    "collab-verified-review/skills/collab-static-verify/SKILL.md",
                    "collab-verified-review/skills/collab-ui-verify/SKILL.md",
                    "collab-verified-review/skills/collab-review-report/SKILL.md",
                },
            )
            self.assertIn("collab-verified-review/assets/cdp-bridge-extension/manifest.json", members)
            self.assertIn("collab-verified-review/skills/collab-verified-review/scripts/fetch_issue.js", members)
            self.assertIn(
                "collab-verified-review/skills/collab-verified-review/references/"
                "project-knowledge-integration.md",
                members,
            )

    def test_orchestrator_explicitly_invokes_know_all_agent(self):
        orchestrator = (
            ROOT / "skills" / "collab-verified-review" / "SKILL.md"
        ).read_text(encoding="utf-8")
        integration = (
            ROOT
            / "skills"
            / "collab-verified-review"
            / "references"
            / "project-knowledge-integration.md"
        ).read_text(encoding="utf-8")

        for tool_name in (
            "review_requirement",
            "recall_project_knowledge",
            "add_investigation_evidence",
            "complete_requirement_review",
        ):
            self.assertIn(tool_name, f"{orchestrator}\n{integration}")
        self.assertIn(
            "Do not call Know All Agent's `verify-project-change`",
            integration,
        )


if __name__ == "__main__":
    unittest.main()
