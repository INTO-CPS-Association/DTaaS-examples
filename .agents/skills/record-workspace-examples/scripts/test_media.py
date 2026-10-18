"""Tests of the names and chapter metadata of the videos."""

import unittest

from media import is_example, segment_name
from recorder import chapter_list, chapter_metadata


class SegmentNameTest(unittest.TestCase):
    """Naming the video of a chapter."""

    def test_example_chapter_is_named_after_its_directory(self):
        """An example chapter has the directory name."""
        self.assertEqual(segment_name(5, "Desktop Robotti and RabbitMQ"),
                         "05-drobotti_rmqfmu.mp4")

    def test_retry_gets_a_suffix(self):
        """A retry has the directory name and the attempt."""
        self.assertEqual(segment_name(21, "Water Treatment Plant and OPC-UA (retry 2)"),
                         "21-opc-ua-waterplant-retry-2.mp4")

    def test_setup_chapter_is_named_after_its_title(self):
        """A setup chapter is named after its title."""
        self.assertEqual(segment_name(3, "Start RabbitMQ and InfluxDB services"),
                         "03-start-rabbitmq-and-influxdb-services.mp4")

    def test_examples_and_setup_chapters(self):
        """Retries of examples are examples, setup chapters not."""
        self.assertTrue(is_example("Incubator"))
        self.assertTrue(is_example("Incubator (retry 1)"))
        self.assertFalse(is_example("Get the examples"))


class ChapterMetadataTest(unittest.TestCase):
    """Writing the chapters of a video."""

    CHAPTERS = [(0.0, "Sign in"), (61.5, "Incubator")]

    def test_each_chapter_lasts_until_the_next(self):
        """A chapter ends where the next starts."""
        meta = chapter_metadata(self.CHAPTERS, 100.0)
        self.assertTrue(meta.startswith(";FFMETADATA1\n"))
        self.assertIn("START=0\nEND=61500\ntitle=Sign in", meta)
        self.assertIn("START=61500\nEND=100000\ntitle=Incubator", meta)

    def test_chapter_list(self):
        """chapters.txt lists start times and titles."""
        self.assertEqual(chapter_list(self.CHAPTERS),
                         "00:00:00 Sign in\n00:01:01 Incubator\n")


if __name__ == "__main__":
    unittest.main()
