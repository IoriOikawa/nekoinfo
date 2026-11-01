"""Run under a real GTK display (CI uses Xvfb), never silently skip failures."""
import cairo
from gi.repository import GLib
from nekoinfo.app import NekoApplication

app = NekoApplication()
assert app.register(None)
app.activate()
window = app.window
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
window.close()
while GLib.MainContext.default().pending():
    GLib.MainContext.default().iteration(False)
assert window.timer_id == 0
assert GLib.MainContext.default().find_source_by_id(source) is None
print('GTK smoke: sampled, drew all charts, reused window, closed and removed timer')
