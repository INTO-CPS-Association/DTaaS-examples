"""Tests of choosing the chapters of several takes for one set of videos."""

import json
import tempfile
import unittest
from pathlib import Path

from assemble import assemble, example_chapters, has_evidence, setup_chapters

SETUP = [("01-sign-in", "Sign in and open the workspace desktop"),
         ("02-get-the-examples", "Get the examples")]


def make_take(root, name, chapters, report):
    """A take directory with the given chapters (stem, title) and evidence."""
    take = root / name
    for sub in ("segments", "web/segments", "gif"):
        (take / sub).mkdir(parents=True)
    rows = ["file\tstart\tduration\ttitle"]
    for stem, title in chapters:
        rows.append(f"{stem}.mp4\t00:00:00\t00:01:00\t{title}")
        for sub, suffix in (("segments", ".mp4"), ("web/segments", ".mp4"), ("gif", ".gif")):
            (take / sub / f"{stem}{suffix}").write_text(name, encoding="utf-8")
    (take / "segments" / "index.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (take / "report.json").write_text(json.dumps(report), encoding="utf-8")
    return take


class AssembleTest(unittest.TestCase):
    """Choosing and copying chapters."""

    def setUp(self):
        """Three takes: all examples, a failed flex-cell retake, a good one."""
        self.root = Path(tempfile.mkdtemp())
        self.first = make_take(self.root, "take1", SETUP + [
            ("03-mass-spring-damper", "Mass Spring Damper"),
            ("04-flex-cell", "Flex Cell with Two Industrial Robots")],
            [{"example": "mass-spring-damper", "evidence": "10002"},
             {"example": "flex-cell", "evidence": "35"}])
        self.failed = make_take(self.root, "take2", SETUP + [
            ("03-flex-cell", "Flex Cell with Two Industrial Robots")],
            [{"example": "flex-cell", "evidence": "0"}])
        self.good = make_take(self.root, "take3", SETUP + [
            ("03-flex-cell", "Flex Cell with Two Industrial Robots")],
            [{"example": "flex-cell", "evidence": "54"}])

    def test_evidence(self):
        """Empty or zero evidence and failed checks do not count."""
        self.assertTrue(has_evidence({"evidence": "resultFI.png"}))
        self.assertFalse(has_evidence({"evidence": "0"}))
        self.assertFalse(has_evidence({"check": "OpenModelica download failed"}))
        self.assertFalse(has_evidence(None))

    def test_setup_comes_before_the_first_example(self):
        """The setup chapters are the ones before the first example."""
        self.assertEqual([title for _, _, title in setup_chapters(self.first)],
                         [title for _, title in SETUP])

    def test_latest_take_with_evidence_wins(self):
        """A later take replaces an example only when it has evidence."""
        chosen = {title: take.name for take, _, title in
                  example_chapters([self.first, self.good, self.failed])}
        self.assertEqual(chosen["Flex Cell with Two Industrial Robots"], "take3")
        self.assertEqual(chosen["Mass Spring Damper"], "take1")

    def test_without_evidence_the_latest_take_wins(self):
        """When no take has evidence, the latest one is used."""
        chosen = example_chapters([self.failed])
        self.assertEqual(chosen[0][0].name, "take2")

    def test_files_are_copied_and_numbered(self):
        """Chapters are numbered again and keep their files and evidence."""
        out = self.root / "all"
        index = assemble(out, [self.first, self.good])
        self.assertEqual([new for new, _, _ in index],
                         ["01-sign-in", "02-get-the-examples",
                          "03-mass-spring-damper", "04-flex-cell"])
        self.assertEqual((out / "gif" / "04-flex-cell.gif").read_text(encoding="utf-8"), "take3")
        report = json.loads((out / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report[-1], {"example": "flex-cell", "evidence": "54", "take": "take3"})


if __name__ == "__main__":
    unittest.main()
