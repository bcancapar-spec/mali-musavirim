#!/usr/bin/env python3
"""Repository-level tests for the Claude Code compatibility layer."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class ClaudeCodeIntegrationTests(unittest.TestCase):
    def test_project_instructions_are_present_and_compact(self) -> None:
        instructions = (PROJECT_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(instructions.splitlines()), 200)
        normalized = instructions.casefold()
        for required in (
            "decimal.Decimal",
            "mükellef lehine",
            "BLOCK",
            "hassas veri",
            "test_suite_report.py",
        ):
            self.assertIn(required.casefold(), normalized)

    def test_three_project_skills_route_to_canonical_skills(self) -> None:
        expected = {
            "muhasebecim": "skills/muhasebecim/SKILL.md",
            "vergi-mufettisi": "skills/vergi-mufettisi/SKILL.md",
            "yeminli-mali-musavir": "skills/yeminli-mali-musavir/SKILL.md",
        }
        skill_root = PROJECT_ROOT / ".claude" / "skills"
        discovered = sorted(path.parent.name for path in skill_root.glob("*/SKILL.md"))
        self.assertEqual(discovered, sorted(expected))
        for skill_name, canonical_path in expected.items():
            content = (skill_root / skill_name / "SKILL.md").read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---\n"))
            frontmatter = content.split("---", 2)[1]
            self.assertRegex(frontmatter, rf"(?m)^name:\s*{re.escape(skill_name)}\s*$")
            self.assertRegex(frontmatter, r"(?m)^description:\s*\S")
            self.assertIn(canonical_path, content)
            self.assertTrue((PROJECT_ROOT / canonical_path).is_file())

    def test_claude_code_guide_and_readme_are_linked(self) -> None:
        guide_path = PROJECT_ROOT / "docs" / "CLAUDE-CODE-KULLANIM-REHBERI.md"
        guide = guide_path.read_text(encoding="utf-8")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/CLAUDE-CODE-KULLANIM-REHBERI.md", readme)
        for official_url in (
            "https://code.claude.com/docs/en/getting-started",
            "https://code.claude.com/docs/en/memory",
            "https://code.claude.com/docs/en/slash-commands",
            "https://code.claude.com/docs/en/permissions",
            "https://code.claude.com/docs/en/data-usage",
        ):
            self.assertIn(official_url, guide)

    def test_networked_model_boundary_is_explicit(self) -> None:
        guide = (
            PROJECT_ROOT / "docs" / "CLAUDE-CODE-KULLANIM-REHBERI.md"
        ).read_text(encoding="utf-8")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Yerel Python hesabı", guide)
        self.assertIn("model bağlamına girebilir", guide)
        self.assertIn("model bağlamına girebilir", readme)
        self.assertIn("Varsayılan olarak Claude Code'a okutmayın", guide)


if __name__ == "__main__":
    unittest.main()
