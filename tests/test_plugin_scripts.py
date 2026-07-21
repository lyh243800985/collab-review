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
    def test_example_review_passes_evidence_gate(self):
        payload = json.loads((ROOT / "assets" / "example-review.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_review.validate(payload), [])

    def test_verified_defect_requires_attribution_and_evidence(self):
        payload = {"scope": {}, "checks": [], "findings": [{"class": "verified_defect", "surface": "ui"}]}
        errors = validate_review.validate(payload)
        self.assertTrue(any("changedLocation" in error for error in errors))
        self.assertTrue(any("evidence" in error for error in errors))

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
                    "collab-verified-review/skills/collab-static-verify/SKILL.md",
                    "collab-verified-review/skills/collab-ui-verify/SKILL.md",
                    "collab-verified-review/skills/collab-review-report/SKILL.md",
                },
            )
            self.assertIn("collab-verified-review/assets/cdp-bridge-extension/manifest.json", members)
            self.assertIn("collab-verified-review/skills/collab-verified-review/scripts/fetch_issue.js", members)


if __name__ == "__main__":
    unittest.main()
