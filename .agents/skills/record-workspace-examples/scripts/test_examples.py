"""Tests that the examples of the recording match the examples of the repository."""

import unittest
from pathlib import Path

import examples
from checks import CHECKS, check_after

REPO = Path(__file__).resolve().parents[4]


class ExamplesTest(unittest.TestCase):
    """The examples and their steps."""

    def test_every_example_is_in_the_repository(self):
        """Each example is a directory of digital_twins."""
        for name, _, _ in examples.EXAMPLES:
            self.assertTrue((REPO / "digital_twins" / name).is_dir(), name)

    def test_names_and_titles_are_unique(self):
        """Names and titles identify the examples and chapters."""
        names = [name for name, _, _ in examples.EXAMPLES]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(examples.TITLES), len(examples.EXAMPLES))

    def test_lifecycle_scripts_exist(self):
        """Every lifecycle script typed in the recording exists."""
        for example in examples.EXAMPLES:
            for command, _ in examples.steps(example):
                if command.startswith("lifecycle/"):
                    script = command.split()[0]
                    path = REPO / "digital_twins" / example[0] / script
                    self.assertTrue(path.is_file(), f"{example[0]}: {script}")

    def test_steps_start_in_the_example_directory(self):
        """The steps start with a cd and the title."""
        name, title, _ = examples.EXAMPLES[0]
        steps = examples.steps(examples.EXAMPLES[0])
        self.assertEqual(steps[0], (f"cd /workspace/examples/digital_twins/{name} && clear", {}))
        self.assertEqual(steps[1], (f"# ===== {title} =====", {}))
        self.assertTrue(all(isinstance(options, dict) for _, options in steps))

    def test_incubator_examples_configure_their_own_copy(self):
        """A copied incubator configuration points at the services."""
        for name, _, items in examples.EXAMPLES:
            if any(str(item).startswith("cp ../incubator/simulation.conf") for item in items):
                self.assertIn(examples.use_services("simulation.conf"), items, name)


class ChecksTest(unittest.TestCase):
    """The evidence collected for every example."""

    def test_every_example_has_a_check(self):
        """Every example and only these have a check."""
        self.assertEqual(set(CHECKS), set(examples.TITLES.values()))

    def test_every_check_follows_a_step_of_its_example(self):
        """A check runs after a step the example has."""
        for example in examples.EXAMPLES:
            commands = [command for command, _ in examples.steps(example)]
            self.assertIn(CHECKS[example[0]][0], commands, example[0])

    def test_check_after_other_steps_is_none(self):
        """No check runs after the other steps."""
        self.assertIsNone(check_after("mass-spring-damper", "lifecycle/create"))
        self.assertIsNotNone(check_after("mass-spring-damper", "lifecycle/execute"))


if __name__ == "__main__":
    unittest.main()
