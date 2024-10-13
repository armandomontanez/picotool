"""A script to ensure version strings are updated across the repo."""

import os
from pathlib import Path
import re
import sys
import subprocess
import unittest

_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def build_bazel_dep_regex(module_name):
    return re.compile(r'bazel_dep\(\s*name\s*=\s*"' + module_name + r'"\s*,\s*version\s*=\s*"(?P<val>.*)"\s*,?\s*')

def build_bazel_module_regex(module_name):
    return re.compile(r'module\(\s*name\s*=\s*"' + module_name + r'"\s*,\s*version\s*=\s*"(?P<val>.*)"\s*,?\s*')

class RegexExtractor:
    def __init__(self, file_path, patterns):
        with file_path.open() as f:
            file_contents = f.read()
            for key, pattern in patterns.items():
                match = pattern.search(file_contents)
                if not match:
                    raise ValueError(f'Failed to find {key} regex in file')
                setattr(self, key, match.group(1))

class VersionCheckTests(unittest.TestCase):
    def setUp(self):
        repo_root = Path(subprocess.run(
            (
                "git",
                "rev-parse",
                "--show-toplevel",
            ),
            cwd=_SCRIPT_DIR,
            text=True,
            check=True,
            capture_output=True,
        ).stdout.strip())
        bazel_patterns = {
            "pico_sdk_min_version": build_bazel_dep_regex("pico-sdk"),
            "project_version": build_bazel_module_regex("picotool"),
        }
        cmake_patterns = {
            "pico_sdk_min_version": re.compile(r'PICO_SDK_VERSION_STRING VERSION_LESS "(?P<val>[^"]*)"'),
            "project_version": re.compile(r'set\(PROJECT_VERSION (?P<val>[^\)]*)\)'),
            "picotool_version": re.compile(r'set\(PICOTOOL_VERSION (?P<val>[^\)]*)\)'),
        }
        self.bazel_info = RegexExtractor(repo_root / "MODULE.bazel", bazel_patterns)
        self.cmake_info = RegexExtractor(repo_root / "CMakeLists.txt", cmake_patterns)

    def test_cmake_versions_match(self):
        """Ensure CMake PROJECT_VERSION and PICOTOOL_VERSION match."""
        self.assertEqual(
            self.cmake_info.project_version,
            self.cmake_info.picotool_version,
        )

    def test_cmake_and_bazel_versions_match(self):
        """Ensure CMake and Bazel declared Picotool versions match."""
        self.assertEqual(
            self.bazel_info.project_version,
            self.cmake_info.project_version,
        )

    def test_min_pico_sdk_versions_match(self):
        """Ensure CMake and Bazel minimum required version for Pico SDK match."""
        self.assertEqual(
            self.bazel_info.pico_sdk_min_version,
            self.cmake_info.pico_sdk_min_version,
        )

if __name__ == '__main__':
    unittest.main()
