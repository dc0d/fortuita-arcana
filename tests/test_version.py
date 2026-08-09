import contextlib
import io
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


class SetVersionTest(TempTreeTest):
    def test_updates_every_spot(self):
        make_tree(self.root)
        previous = version.set_version(self.root, "0.2.0")
        self.assertEqual(previous, "0.1.0")
        self.assertEqual(version.current_version(self.root), "0.2.0")
        for path, _ in version.SPOTS:
            self.assertIn('"0.2.0"', (self.root / path).read_text())

    def test_rewrite_is_byte_stable_except_version(self):
        make_tree(self.root)
        marketplace = self.root / ".github/plugin/marketplace.json"
        expected = marketplace.read_text().replace("0.1.0", "0.2.0")
        version.set_version(self.root, "0.2.0")
        self.assertEqual(marketplace.read_text(), expected)

    def test_rejects_equal_version(self):
        make_tree(self.root)
        with self.assertRaises(version.VersionError):
            version.set_version(self.root, "0.1.0")

    def test_rejects_lower_version(self):
        make_tree(self.root)
        with self.assertRaises(version.VersionError):
            version.set_version(self.root, "0.0.9")

    def test_rejects_malformed_version(self):
        make_tree(self.root)
        with self.assertRaises(version.VersionError):
            version.set_version(self.root, "v0.2.0")

    def test_refuses_to_write_on_drift(self):
        make_tree(self.root, entry="0.2.0")
        claude_manifest = self.root / "plugins/fortuita-arcana/.claude-plugin/plugin.json"
        before = claude_manifest.read_text()
        with self.assertRaises(version.VersionError):
            version.set_version(self.root, "0.3.0")
        self.assertEqual(claude_manifest.read_text(), before)


class CliTest(TempTreeTest):
    def run_cli(self, *argv):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = version.main(["--root", str(self.root), *argv])
        return code, stdout.getvalue(), stderr.getvalue()

    def test_check_prints_version(self):
        make_tree(self.root)
        code, out, err = self.run_cli("check")
        self.assertEqual((code, out, err), (0, "0.1.0\n", ""))

    def test_set_reports_transition(self):
        make_tree(self.root)
        code, out, err = self.run_cli("set", "0.2.0")
        self.assertEqual((code, out, err), (0, "0.1.0 -> 0.2.0\n", ""))
        self.assertEqual(version.current_version(self.root), "0.2.0")

    def test_errors_exit_nonzero_via_stderr(self):
        make_tree(self.root, entry="9.9.9")
        code, out, err = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("drift", err)


if __name__ == "__main__":
    unittest.main()
