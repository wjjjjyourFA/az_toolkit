import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

from az_toolkit.common import misc
from az_toolkit.dataset.timestamp_match import match_timestamp_image
from az_toolkit.pointcloud.laser_scan import LaserScan


class TimestampMatchTests(unittest.TestCase):
    def test_empty_catch_sequence_is_unmatched(self):
        matched, unmatched = match_timestamp_image([100], [], time_threshold=10)
        self.assertEqual(matched, [])
        self.assertEqual(unmatched, [100])

    def test_exhausted_catch_sequence_does_not_overrun(self):
        matched, unmatched = match_timestamp_image([100, 200], [95], time_threshold=10)
        self.assertEqual(matched, [95])
        self.assertEqual(unmatched, [200])


class LaserScanProjectionTests(unittest.TestCase):
    def test_first_point_index_is_marked_valid(self):
        scan = LaserScan(height=4, width=8, fov_up=10.0, fov_down=-10.0)
        scan.set_points(
            np.array([[1.0, 0.0, 0.0]], dtype=np.float32),
            np.array([0.5], dtype=np.float32),
        )
        scan.do_range_projection()
        self.assertEqual(int(scan.proj_mask.sum()), 1)
        self.assertIn(0, scan.proj_idx[scan.proj_mask.astype(bool)])


class AtomicWriteTests(unittest.TestCase):
    def test_replace_failure_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "labels.txt"
            target.write_text("old\n", encoding="utf-8")

            with mock.patch.object(misc.os, "replace", side_effect=OSError("injected")):
                with self.assertRaises(OSError):
                    misc.atomic_write_text(target, "new\n")

            self.assertEqual(target.read_text(encoding="utf-8"), "old\n")
            self.assertEqual(list(Path(directory).glob(".labels.txt.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
