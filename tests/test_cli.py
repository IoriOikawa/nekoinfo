import os
import subprocess
import sys
import unittest
from contextlib import redirect_stderr
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from nekoinfo.__main__ import main


class CliTests(unittest.TestCase):
    def renderer_at_gtk_import(self, platform, renderer=None):
        observed = []

        def require_version(*args):
            observed.append(os.environ.get('GSK_RENDERER'))
            raise ImportError('stop before loading native GUI libraries')

        environment = {} if renderer is None else {'GSK_RENDERER': renderer}
        gi = SimpleNamespace(require_version=require_version)
        with patch.dict(os.environ, environment, clear=True), \
                patch.dict(sys.modules, {'gi': gi}), \
                patch.object(sys, 'platform', platform), \
                patch.object(sys, 'argv', ['nekoinfo']), \
                redirect_stderr(StringIO()):
            self.assertEqual(main(), 1)
        self.assertEqual(len(observed), 1)
        return observed[0]

    def test_linux_defaults_to_cairo_before_loading_gtk(self):
        self.assertEqual(self.renderer_at_gtk_import('linux'), 'cairo')

    def test_explicit_renderer_is_preserved(self):
        for renderer in ('gl', 'vulkan', 'cairo', ''):
            with self.subTest(renderer=renderer):
                self.assertEqual(self.renderer_at_gtk_import('linux', renderer), renderer)

    def test_other_platforms_keep_native_renderer(self):
        for platform in ('darwin', 'win32'):
            with self.subTest(platform=platform):
                self.assertIsNone(self.renderer_at_gtk_import(platform))

    def test_version_without_importing_gtk(self):
        result = subprocess.run([sys.executable, '-m', 'nekoinfo', '--version'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'Neko Info 2.0.0')
