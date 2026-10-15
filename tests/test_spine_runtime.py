from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "spine_runtime", ROOT / "scripts/spine.py"
)
assert SPEC and SPEC.loader
SPINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SPINE)


class GeneratedSpineRuntimeTests(unittest.TestCase):
    def test_manifest_loads(self) -> None:
        path, manifest = SPINE.load_manifest(ROOT)
        self.assertEqual(path, ROOT / ".spine" / "manifest.json")
        self.assertEqual(manifest["schemaVersion"], 1)
        self.assertFalse(
            manifest["capabilityPolicy"]["scriptsAreExclusiveAllowList"]
        )
        self.assertEqual(SPINE.validate_github_policy(ROOT, manifest), [])
        self.assertEqual(
            manifest["githubPolicy"]["releaseAuthority"], "supplemental"
        )
        self.assertFalse(manifest["githubPolicy"]["automaticPublish"])
        self.assertEqual(SPINE.validate_github_action_pins(ROOT), [])
        with mock.patch.object(SPINE, "run_commands", return_value=0) as commands:
            self.assertEqual(SPINE.command_release_plan(ROOT, manifest), 0)
            commands.assert_called_once()

    def test_ecosystem_is_pinned_and_manual(self) -> None:
        _, manifest = SPINE.load_manifest(ROOT)
        path, catalog = SPINE.load_ecosystem(ROOT, manifest)
        self.assertEqual(path, ROOT / ".spine" / "ecosystem.json")
        self.assertIsNotNone(catalog)
        assert catalog is not None
        self.assertEqual(SPINE.validate_ecosystem(ROOT, manifest), [])
        self.assertEqual(catalog["defaults"]["activation"], "off")
        self.assertFalse(catalog["defaults"]["autoInstall"])
        self.assertFalse(catalog["defaults"]["autoUpdate"])
        for source in catalog["sources"]:
            self.assertEqual(len(source["pin"]["revision"]), 40)
            self.assertFalse(source["autoInstall"])
        routed = [route["capability"] for route in catalog["routes"]]
        self.assertEqual(len(routed), len(set(routed)))

    def test_release_plan_fails_closed_without_github_policy(self) -> None:
        _, manifest = SPINE.load_manifest(ROOT)
        manifest = copy.deepcopy(manifest)
        manifest.pop("githubPolicy")
        self.assertEqual(SPINE.command_release_plan(ROOT, manifest), 1)

    def test_github_policy_authority_stays_inside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            outer = Path(temporary)
            root = outer / "repository"
            (root / "docs").mkdir(parents=True)
            outside = outer / "outside-policy.md"
            outside.write_text("# Outside policy\n", encoding="utf-8")
            _, manifest = SPINE.load_manifest(ROOT)
            manifest = copy.deepcopy(manifest)

            for authority in (f"../{outside.name}", str(outside)):
                manifest["githubPolicy"]["authority"] = authority
                self.assertIn(
                    "github policy authority must stay within the repository",
                    SPINE.validate_github_policy(root, manifest),
                )

            symlink = root / "docs" / "outside-policy-link.md"
            symlink.symlink_to(outside)
            manifest["githubPolicy"]["authority"] = str(
                symlink.relative_to(root)
            )
            self.assertIn(
                "github policy authority must stay within the repository",
                SPINE.validate_github_policy(root, manifest),
            )


if __name__ == "__main__":
    unittest.main()
