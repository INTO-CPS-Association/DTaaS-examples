"""Tests of the speed plan of the web videos."""

import unittest

from speed import Speeds, log_steps, played, speed_plan

LOG = """\
[00:00:00] recording to /opt/recording/dtaas-workspace-examples.mkv
[00:00:03] CHAPTER Mass Spring Damper
[00:00:03] mass-spring-damper: cd /workspace/examples/digital_twins/mass-spring-damper && clear
[00:00:13] mass-spring-damper: lifecycle/create
[00:01:53] mass-spring-damper: lifecycle/execute
[00:02:03] mass-spring-damper evidence: 10002
[00:02:03] mass-spring-damper: head -5 outputs.csv
[00:02:13] pressing Ctrl+C
[00:02:13] mass-spring-damper: firefox --new-window plot.png & sleep 20; pkill -x firefox
[00:05:13] CHAPTER Done
"""


class LogStepsTest(unittest.TestCase):
    """Reading the steps from driver.log."""

    def test_steps_and_chapters(self):
        """Steps and chapters come with their seconds."""
        steps = log_steps(LOG)
        self.assertEqual(steps[0], (3, None))
        self.assertEqual(steps[2], (13, "lifecycle/create"))
        self.assertEqual(steps[-1], (313, None))

    def test_evidence_and_notes_are_not_steps(self):
        """Evidence and notes do not end a step."""
        commands = [command for _, command in log_steps(LOG)]
        self.assertNotIn("evidence: 10002", commands)
        self.assertEqual(len(commands), 7)


class SpeedPlanTest(unittest.TestCase):
    """Choosing the speed of each part of a chapter."""

    def setUp(self):
        """The plan of the chapter in LOG."""
        self.plan = speed_plan((3, 313), log_steps(LOG))

    def test_parts_cover_the_chapter(self):
        """The parts cover the chapter without gaps."""
        self.assertEqual(self.plan[0][0], 3)
        self.assertEqual(self.plan[-1][1], 313)
        for before, after in zip(self.plan, self.plan[1:]):
            self.assertEqual(before[1], after[0])

    def test_long_step_plays_fast_and_short_step_normally(self):
        """Long steps play fast, short ones normally."""
        self.assertIn((3, 13, 4), self.plan)
        self.assertIn((13, 113, 16), self.plan)

    def test_results_play_at_result_speed_for_a_limited_time(self):
        """Results play slowly, but not for long."""
        self.assertIn((123, 193, 1), self.plan)
        self.assertEqual(self.plan[-1], (193, 313, 16))

    def test_adjacent_equal_speeds_are_merged(self):
        """Neighbouring parts have different speeds."""
        speeds = [speed for _, _, speed in self.plan]
        self.assertTrue(all(a != b for a, b in zip(speeds, speeds[1:])))

    def test_a_short_part_joins_its_neighbour(self):
        """A part too short for frames joins its neighbour."""
        plan = speed_plan((0, 10.1), [(0, "a"), (10, "head -5 x")], Speeds())
        self.assertEqual(plan, [(0, 10.1, 4)])

    def test_played_time(self):
        """The played time of parts."""
        self.assertAlmostEqual(played([(0, 40, 4), (40, 200, 16)]), 20)


if __name__ == "__main__":
    unittest.main()
