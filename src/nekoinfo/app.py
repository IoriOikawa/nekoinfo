"""GTK4 presentation. A single GLib source belongs to each live window."""
import gi
gi.require_version('Gtk', '4.0')
gi.require_foreign('cairo')
from gi.repository import Gtk, GLib
from .autostart import Autostart
from .charts import Trend
from .metrics import History, Sampler
from .theme import SystemTheme, connect_portal


def size(value):
    return f'{value / 1024 ** 3:.1f} GiB'


def rate(value):
    return f'{value / 1024 ** 2:.1f} MiB/s' if value >= 1024 ** 2 else f'{value / 1024:.1f} KiB/s'


class NekoWindow(Gtk.ApplicationWindow):
    def __init__(self, application):
        super().__init__(application=application, title='Neko Info')
        self.set_default_size(360, -1)
        self.set_icon_name('nekoinfo')
        # Some themes give switches a zero font size. GTK 4.14 derives the
        # internal images' baselines from that font, so give just our images
        # a nonzero font without changing the theme's colors or geometry.
        self.style_provider = Gtk.CssProvider()
        self.style_provider.load_from_data(
            b'switch.nekoinfo-startup-switch > image { font-size: 13px; }')
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), self.style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.sampler, self.history = Sampler(), History()
        self.timer_id = 0
        self.autostart = Autostart()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        for side in ('top', 'bottom', 'start', 'end'):
            getattr(box, f'set_margin_{side}')(16)
        self.set_child(box)
        title = Gtk.Label(label='ฅ^•ﻌ•^ฅ   Neko Info', xalign=0)
        title.add_css_class('title-3')
        box.append(title)
        self.charts = []
        self.labels = {}
        for name, accessor, ceiling in (
            ('CPU', lambda s: s.cpu_percent, 100),
            ('Memory', lambda s: s.memory.percent if s.memory else None, 100),
            ('Download ↓', lambda s: s.network.received if s.network else None, None),
            ('Upload ↑', lambda s: s.network.sent if s.network else None, None),
        ):
            label = Gtk.Label(label=f'{name}   Waiting…', xalign=0)
            self.labels[name] = label
            box.append(label)
            chart = Trend(self.history, accessor, ceiling)
            self.charts.append(chart)
            box.append(chart)
        self.labels['Memory'].set_tooltip_text('Used = total − available. Available includes reclaimable caches; it is not just free RAM.')
        network_tip = 'Aggregate of non-loopback interfaces. VPNs, bridges and virtual interfaces can count traffic more than once; this is not exact Internet bandwidth.'
        self.labels['Download ↓'].set_tooltip_text(network_tip)
        self.labels['Upload ↑'].set_tooltip_text(network_tip)
        self.cores = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.core_labels = []
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(120)
        scroll.set_max_content_height(180)
        scroll.set_propagate_natural_height(True)
        scroll.set_child(self.cores)
        self.expander = Gtk.Expander(label='Logical processors')
        self.expander.set_child(scroll)
        box.append(self.expander)
        startup = Gtk.Box(spacing=12)
        startup.append(Gtk.Label(label='Start at login', hexpand=True, xalign=0))
        self.switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.switch.add_css_class('nekoinfo-startup-switch')
        self.startup_error = Gtk.Label(xalign=0, wrap=True)
        self.startup_error.add_css_class('error')
        try:
            self.switch.set_active(self.autostart.enabled())
        except OSError as error:
            self.startup_error.set_text(str(error))
        self.switch.connect('state-set', self.set_startup)
        startup.append(self.switch)
        box.append(startup)
        box.append(self.startup_error)
        self.connect('close-request', self.on_close)
        self.refresh()
        self.timer_id = GLib.timeout_add_seconds(2, self.refresh)

    def set_startup(self, switch, enabled):
        try:
            self.autostart.set_enabled(enabled)
        except OSError as error:
            self.startup_error.set_text(str(error))
            switch.set_active(switch.get_state())
            return True
        self.startup_error.set_text('')
        return False

    def refresh(self):
        sample = self.sampler.sample()
        self.history.append(sample)
        def missing(metric):
            return 'Unavailable' if metric in sample.errors else 'Waiting…'
        cpu = f'{sample.cpu_percent:.0f}%' if sample.cpu_percent is not None else missing('cpu')
        self.labels['CPU'].set_text(f'CPU   {cpu}')
        memory = sample.memory
        self.labels['Memory'].set_text(
            f'Memory   {memory.percent:.0f}% · {size(memory.used)} / {size(memory.total)}\nAvailable {size(memory.available)}'
            if memory else f'Memory   {missing("memory")}')
        for label, value in (('Download ↓', sample.network.received if sample.network else None),
                             ('Upload ↑', sample.network.sent if sample.network else None)):
            self.labels[label].set_text(f'{label}   {rate(value) if value is not None else missing("network")}')
        values = sample.per_cpu or ()
        while len(self.core_labels) < len(values):
            label = Gtk.Label(xalign=0)
            self.core_labels.append(label)
            self.cores.append(label)
        while len(self.core_labels) > len(values):
            self.cores.remove(self.core_labels.pop())
        for index, (label, value) in enumerate(zip(self.core_labels, values)):
            label.set_text(f'CPU {index + 1}   {value:.0f}%')
        for chart in self.charts:
            chart.queue_draw()
        return GLib.SOURCE_CONTINUE

    def on_close(self, *args):
        if self.timer_id:
            GLib.source_remove(self.timer_id)
            self.timer_id = 0
        if self.style_provider is not None:
            Gtk.StyleContext.remove_provider_for_display(
                self.get_display(), self.style_provider)
            self.style_provider = None
        self.get_application().window = None
        return False


class NekoApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='io.github.paperneko.NekoInfo')
        self.window = None
        self.theme = None

    def do_activate(self):
        settings = Gtk.Settings.get_default()
        if self.theme is None and not settings.find_property("gtk-interface-color-scheme"):
            self.theme = SystemTheme(settings, connect_portal)
        if self.window is None:
            self.window = NekoWindow(self)
        self.window.present()

    def do_shutdown(self):
        if self.theme is not None:
            self.theme.close()
            self.theme = None
        if self.window is not None:
            self.window.on_close()
        Gtk.Application.do_shutdown(self)
