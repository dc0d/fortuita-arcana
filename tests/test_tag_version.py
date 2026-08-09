import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "tag-version.sh"

# Hermetic git: ignore the developer's global/system config (hooks, signing).
ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_SYSTEM": "/dev/null",
}


def run(args, cwd, check=True):
    result = subprocess.run(args, cwd=cwd, env=ENV, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise AssertionError(f"{args} failed:\n{result.stdout}\n{result.stderr}")
    return result


class TagVersionScriptTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        base = Path(self._tmp.name)
        self.remote = base / "remote.git"
        self.repo = base / "repo"
        run(["git", "init", "--bare", str(self.remote)], cwd=base)
        run(["git", "clone", str(self.remote), str(self.repo)], cwd=base)
        run(["git", "config", "user.name", "Test"], cwd=self.repo)
        run(["git", "config", "user.email", "test@example.com"], cwd=self.repo)
        self.commit("first commit")

    def commit(self, message):
        notes = self.repo / "notes.txt"
        with notes.open("a") as handle:
            handle.write(message + "\n")
        run(["git", "add", "."], cwd=self.repo)
        run(["git", "commit", "-m", message], cwd=self.repo)

    def tag_script(self, version_arg):
        return run(["bash", str(SCRIPT), version_arg], cwd=self.repo, check=False)

    def test_creates_and_pushes_annotated_tag(self):
        result = self.tag_script("0.1.0")
        self.assertEqual(result.returncode, 0, result.stderr)
        kind = run(["git", "cat-file", "-t", "v0.1.0"], cwd=self.repo).stdout.strip()
        self.assertEqual(kind, "tag")  # annotated, not lightweight
        remote_tags = run(["git", "ls-remote", "--tags", "origin"], cwd=self.repo).stdout
        self.assertIn("refs/tags/v0.1.0", remote_tags)
        message = run(["git", "cat-file", "tag", "v0.1.0"], cwd=self.repo).stdout
        self.assertIn("Release 0.1.0", message)
        self.assertIn("Initial release:", message)
        self.assertIn("first commit", message)

    def test_rerun_is_a_noop(self):
        self.tag_script("0.1.0")
        result = self.tag_script("0.1.0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("already exists", result.stdout)

    def test_changelog_spans_since_previous_tag(self):
        self.tag_script("0.1.0")
        self.commit("second commit")
        result = self.tag_script("0.2.0")
        self.assertEqual(result.returncode, 0, result.stderr)
        message = run(["git", "cat-file", "tag", "v0.2.0"], cwd=self.repo).stdout
        self.assertIn("Changes since v0.1.0:", message)
        self.assertIn("second commit", message)
        self.assertNotIn("first commit", message)

    def test_refuses_version_lower_than_highest_tag(self):
        self.tag_script("0.2.0")
        self.commit("second commit")
        result = self.tag_script("0.1.5")
        self.assertEqual(result.returncode, 1)
        self.assertIn("not greater", result.stderr)

    def test_numeric_comparison_not_lexicographic(self):
        self.tag_script("0.9.0")
        self.commit("second commit")
        result = self.tag_script("0.10.0")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_v_prefixed_argument(self):
        result = self.tag_script("v0.1.0")
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid version", result.stderr)

    def test_requires_exactly_one_argument(self):
        result = run(["bash", str(SCRIPT)], cwd=self.repo, check=False)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
