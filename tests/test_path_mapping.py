import os
from pathlib import Path
import unittest
from unittest.mock import patch

from src.path_mapping import PATH_MAP_ENV, map_configured_path


class PathMappingTests(unittest.TestCase):
    def test_returns_original_path_without_configuration(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(map_configured_path("/host/code/action"), "/host/code/action")

    def test_maps_exact_prefix(self):
        with patch.dict(os.environ, {PATH_MAP_ENV: "/host/code=/pipeline/code"}):
            self.assertEqual(map_configured_path("/host/code"), "/pipeline/code")

    def test_maps_child_path_and_normalizes_source_separators(self):
        with patch.dict(os.environ, {PATH_MAP_ENV: r"C:\repo\code=/pipeline/code"}):
            expected = str(Path("/pipeline/code", "battery", "status"))
            self.assertEqual(
                map_configured_path(r"C:\repo\code\battery\status"),
                expected,
            )

    def test_does_not_match_partial_directory_name(self):
        with patch.dict(os.environ, {PATH_MAP_ENV: "/host/code=/pipeline/code"}):
            self.assertEqual(
                map_configured_path("/host/code-other/action"),
                "/host/code-other/action",
            )

    def test_skips_invalid_mappings(self):
        path_map = "invalid;=/missing-source;/missing-target=;/host=/pipeline/code"
        with patch.dict(os.environ, {PATH_MAP_ENV: path_map}):
            expected = str(Path("/pipeline/code", "action"))
            self.assertEqual(map_configured_path("/host/action"), expected)


if __name__ == "__main__":
    unittest.main()
