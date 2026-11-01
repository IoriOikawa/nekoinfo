import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from nekoinfo.autostart import Autostart, desktop_exec


class AutostartTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.a = Autostart(self.path, '/opt/Neko Info/bin/neko"info%')
    def test_default_off_then_enable_disable(self):
        self.assertFalse(self.a.enabled())
        self.a.set_enabled(True)
        self.assertTrue(self.a.enabled())
        self.assertIn('X-NekoInfo-Owned=true', self.a.path.read_text())
        self.a.set_enabled(False)
        self.assertFalse(self.a.path.exists())
    def test_exec_quoting(self):
        # Parse both Desktop Entry string escaping and Exec quoted-argument escaping.
        # Percent literals are decoded after field-code expansion.
        import re
        launcher = '/opt/Neko Info/quote"slash\\dollar$backtick`percent%'
        encoded = desktop_exec(launcher)
        self.assertIn('\\\\"', encoded)
        unescaped = re.sub(r'\\(.)', lambda m: m[1], encoded)
        self.assertTrue(unescaped.startswith('"') and unescaped.endswith('"'))
        argument = re.sub(r'\\(.)', lambda m: m[1], unescaped[1:-1]).replace('%%', '%')
        self.assertEqual(argument, launcher)

    def test_respects_xdg(self):
        with patch.dict(os.environ, {'XDG_CONFIG_HOME': str(self.path)}):
            self.assertEqual(Autostart().path, self.path / 'autostart/nekoinfo.desktop')
    def test_never_modifies_unowned_entry(self):
        self.a.path.parent.mkdir()
        self.a.path.write_text('[Desktop Entry]\nName=Other\n')
        for enabled in (True, False):
            with self.assertRaises(FileExistsError): self.a.set_enabled(enabled)
        self.assertIn('Name=Other', self.a.path.read_text())
    def test_invalid_utf8_is_unowned_and_untouched(self):
        self.a.path.parent.mkdir()
        self.a.path.write_bytes(b'\xffother')
        self.assertFalse(self.a.enabled())
        with self.assertRaises(FileExistsError): self.a.set_enabled(True)
        self.assertEqual(self.a.path.read_bytes(), b'\xffother')

    def test_missing_launcher_and_write_error_propagate(self):
        a = Autostart(self.path, None)
        with patch('nekoinfo.autostart.shutil.which', return_value=None):
            with self.assertRaises(FileNotFoundError): a.set_enabled(True)
        self.a.path.parent.write_text('blocked')
        with self.assertRaises(OSError): self.a.set_enabled(True)


if __name__ == '__main__': unittest.main()
