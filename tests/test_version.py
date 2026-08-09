import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import version


def make_tree(root, claude="0.1.0", copilot="0.1.0", meta="0.1.0", entry="0.1.0"):
    """Write the three manifest files carrying the four version spots."""
    claude_manifest = root / "plugins/fortuita-arcana/.claude-plugin/plugin.json"
    copilot_manifest = root / "plugins/fortuita-arcana/plugin.json"
    marketplace = root / ".github/plugin/marketplace.json"
    claude_manifest.parent.mkdir(parents=True)
    marketplace.parent.mkdir(parents=True)
    claude_manifest.write_text(
        json.dumps({"name": "fortuita-arcana", "version": claude}, indent=2) + "\n"
    )
    copilot_manifest.write_text(
        json.dumps({"name": "fortuita-arcana", "version": copilot}, indent=2) + "\n"
    )
    marketplace.write_text(
        json.dumps(
            {
                "name": "fortuita-arcana",
                "metadata": {"description": "x", "version": meta},
                "plugins": [{"name": "fortuita-arcana", "version": entry}],
            },
            indent=2,
        )
        + "\n"
    )


class TempTreeTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)


class ParseVersionTest(unittest.TestCase):
    def test_accepts_release_versions(self):
        self.assertEqual(version.parse_version("0.1.0"), (0, 1, 0))
        self.assertEqual(version.parse_version("10.20.30"), (10, 20, 30))

    def test_rejects_malformed_versions(self):
        bad_values = ["v1.2.3", "1.2", "1.2.3.4", "1.2.3-rc1", "01.2.3",
                      "1.02.3", "", "1.2.x", None]
        for bad in bad_values:
            with self.assertRaises(version.VersionError, msg=repr(bad)):
                version.parse_version(bad)

    def test_ordering_is_numeric_not_lexicographic(self):
        self.assertGreater(
            version.parse_version("0.10.0"), version.parse_version("0.9.0")
        )


class CurrentVersionTest(TempTreeTest):
    def test_returns_version_when_all_spots_agree(self):
        make_tree(self.root)
        self.assertEqual(version.current_version(self.root), "0.1.0")

    def test_drift_error_names_every_spot(self):
        make_tree(self.root, entry="0.2.0")
        with self.assertRaises(version.VersionError) as ctx:
            version.current_version(self.root)
        message = str(ctx.exception)
        self.assertIn("drift", message)
        for path, keys in version.SPOTS:
            self.assertIn(version.spot_label(path, keys), message)

    def test_missing_manifest(self):
        make_tree(self.root)
        (self.root / "plugins/fortuita-arcana/plugin.json").unlink()
        with self.assertRaises(version.VersionError) as ctx:
            version.current_version(self.root)
        self.assertIn("plugins/fortuita-arcana/plugin.json", str(ctx.exception))

    def test_missing_key(self):
        make_tree(self.root)
        marketplace = self.root / ".github/plugin/marketplace.json"
        data = json.loads(marketplace.read_text())
        del data["metadata"]["version"]
        marketplace.write_text(json.dumps(data, indent=2) + "\n")
        with self.assertRaises(version.VersionError) as ctx:
            version.current_version(self.root)
        self.assertIn("metadata.version", str(ctx.exception))

    def test_rejects_invalid_stored_version(self):
        make_tree(self.root, claude="banana", copilot="banana",
                  meta="banana", entry="banana")
        with self.assertRaises(version.VersionError):
            version.current_version(self.root)


if __name__ == "__main__":
    unittest.main()
