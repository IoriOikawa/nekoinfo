"""Run under a real GTK display (CI uses Xvfb), never silently skip failures."""
import os
import tempfile
import cairo
from nekoinfo.app import NekoApplication
from gi.repository import GLib, Gtk

config = tempfile.TemporaryDirectory()
os.environ["XDG_CONFIG_HOME"] = config.name
app = NekoApplication()
assert app.register(None)
app.activate()
window = app.window
# Reproduce the custom theme's zero-font switch rule at user priority.
# Only this application's marked switch images should override inheritance.
theme = Gtk.CssProvider()
theme.load_from_data(b'switch { font-size: 0; }')
Gtk.StyleContext.add_provider_for_display(window.get_display(), theme,
                                        Gtk.STYLE_PROVIDER_PRIORITY_USER)
assert window.switch.has_css_class('nekoinfo-startup-switch')
images = []
child = window.switch.get_first_child()
while child is not None:
    if isinstance(child, Gtk.Image):
        metrics = child.get_pango_context().get_metrics(None, None)
        assert metrics.get_ascent() + metrics.get_descent() > 0
        # A nonzero explicit child font must survive a user-priority parent rule.
        assert child.get_pango_context().get_font_description().get_size() > 0
        images.append(child)
    child = child.get_next_sibling()
assert images
source = window.timer_id
assert source and GLib.MainContext.default().find_source_by_id(source)
app.activate()
assert app.window is window and window.timer_id == source
window.expander.set_expanded(True)
assert window.expander.get_child().get_min_content_height() >= 120
window.refresh()
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 320, 64)
for chart in window.charts:
    chart.draw(chart, cairo.Context(surface), 320, 64)
assert len(window.history.samples) == 2
# A filesystem failure must leave both the active appearance and state off.
class DeniedAutostart:
    def set_enabled(self, enabled):
        raise PermissionError('test write denied')
window.autostart = DeniedAutostart()
window.switch.set_active(True)
assert not window.switch.get_active() and not window.switch.get_state()
assert 'denied' in window.startup_error.get_text()
window.close()
while GLib.MainContext.default().pending():
    GLib.MainContext.default().iteration(False)
assert window.timer_id == 0
assert GLib.MainContext.default().find_source_by_id(source) is None
Gtk.StyleContext.remove_provider_for_display(window.get_display(), theme)
config.cleanup()
print('GTK smoke: sampled, drew all charts, reused window, closed and removed timer')
