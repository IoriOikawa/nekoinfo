"""Desktop appearance portal bridge for GTK versions before 4.20."""


class SystemTheme:
    def __init__(self, settings, connect):
        self.settings = settings
        self.default = settings.get_property('gtk-application-prefer-dark-theme')
        self.closed = False
        self.disconnect = connect(self.update, self.failed)

    def update(self, preference):
        if not self.closed:
            dark = {1: True, 2: False}.get(preference, self.default)
            self.settings.set_property('gtk-application-prefer-dark-theme', dark)

    def failed(self):
        self.update(0)

    def close(self):
        if not self.closed:
            self.closed = True
            self.disconnect()


def connect_portal(update, failed):
    """Read and subscribe asynchronously; return cancellation/disconnection cleanup."""
    from gi.repository import Gio, GLib
    cancellable = Gio.Cancellable()
    proxy = None
    signal_id = 0
    closed = False

    def changed(source, sender, signal, parameters):
        if closed or signal != 'SettingChanged':
            return
        namespace, key, value = parameters.unpack()
        if namespace == 'org.freedesktop.appearance' and key == 'color-scheme':
            update(value.unpack() if hasattr(value, 'unpack') else value)

    def read_done(source, result, *user_data):
        if closed:
            return
        try:
            value = source.call_finish(result).unpack()[0]
            update(value.unpack() if hasattr(value, 'unpack') else value)
        except GLib.Error:
            failed()

    def ready(source, result, *user_data):
        nonlocal proxy, signal_id
        if closed:
            return
        try:
            proxy = Gio.DBusProxy.new_for_bus_finish(result)
            signal_id = proxy.connect('g-signal', changed)
            proxy.call('Read', GLib.Variant('(ss)', ('org.freedesktop.appearance', 'color-scheme')),
                       Gio.DBusCallFlags.NONE, -1, cancellable, read_done)
        except GLib.Error:
            failed()

    Gio.DBusProxy.new_for_bus(Gio.BusType.SESSION, Gio.DBusProxyFlags.DO_NOT_AUTO_START,
                             None, 'org.freedesktop.portal.Desktop',
                             '/org/freedesktop/portal/desktop',
                             'org.freedesktop.portal.Settings', cancellable, ready)

    def disconnect():
        nonlocal closed
        closed = True
        cancellable.cancel()
        if proxy is not None and signal_id:
            proxy.disconnect(signal_id)
    return disconnect
