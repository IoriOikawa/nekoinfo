"""Small, theme-aware Cairo trends using actual sample timestamps."""
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


class Trend(Gtk.DrawingArea):
    def __init__(self, history, value, ceiling=100):
        super().__init__()
        self.history, self.value, self.ceiling = history, value, ceiling
        self.set_content_height(42)
        self.set_hexpand(True)
        self.set_draw_func(self.draw)
        self.set_tooltip_text('Last 60 seconds; gaps indicate waiting, unavailable data or resume.')

    def draw(self, area, cr, width, height):
        color = self.get_style_context().get_color()
        cr.set_source_rgba(color.red, color.green, color.blue, 0.18)
        cr.set_line_width(1)
        cr.move_to(0, height - 1)
        cr.line_to(width, height - 1)
        cr.stroke()
        samples = self.history.samples
        if not samples:
            return
        end = samples[-1].timestamp
        values = [self.value(sample) for sample in samples]
        scale = self.ceiling or max([1024] + [v for v in values if v is not None]) * 1.15
        cr.set_source_rgba(color.red, color.green, color.blue, 0.85)
        cr.set_line_width(1.8)
        previous = None
        for sample, value in zip(samples, values):
            if value is None:
                cr.stroke()
                previous = None
                continue
            x = width * (sample.timestamp - end + 60) / 60
            y = height - 2 - min(max(value / scale, 0), 1) * (height - 4)
            if previous is None or sample.timestamp - previous > 10:
                cr.stroke()
                cr.move_to(x, y)
            else:
                cr.line_to(x, y)
            cr.arc(x, y, 1, 0, 6.283185)
            cr.move_to(x, y)
            previous = sample.timestamp
        cr.stroke()
