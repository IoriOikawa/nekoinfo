import os
import subprocess
import sys
import unittest


class CliTests(unittest.TestCase):
    def test_version_without_importing_gtk(self):
        result = subprocess.run([sys.executable, '-m', 'nekoinfo', '--version'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'Neko Info 2.0.0')
