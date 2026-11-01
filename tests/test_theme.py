import unittest
from nekoinfo.theme import SystemTheme


class Settings:
    def __init__(self): self.dark = False
    def get_property(self, name): return self.dark
    def set_property(self, name, value): self.dark = value


class Portal:
    def connect(self, update, failed):
        self.update, self.failed = update, failed
        self.closed = False
        return self.close
    def close(self): self.closed = True


class ThemeTests(unittest.TestCase):
    def setUp(self):
        self.settings, self.portal = Settings(), Portal()
        self.theme = SystemTheme(self.settings, self.portal.connect)
    def test_portal_dark_light_default_and_unknown(self):
        for value, expected in ((1, True), (2, False), (1, True), (0, False), (8, False)):
            self.portal.update(value)
            self.assertEqual(self.settings.dark, expected)
    def test_unavailable_portal_restores_native_default(self):
        self.portal.update(1)
        self.portal.failed()
        self.assertFalse(self.settings.dark)
    def test_shutdown_cleans_connection_and_ignores_late_callbacks(self):
        self.theme.close()
        self.assertTrue(self.portal.closed)
        self.portal.update(1)
        self.assertFalse(self.settings.dark)
