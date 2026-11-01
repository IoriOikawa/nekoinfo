"""Opt-in desktop session startup, restricted to an application-owned file."""
import os
from pathlib import Path
import shutil
import tempfile

OWNER = 'X-NekoInfo-Owned=true'


def desktop_exec(launcher):
    # Escape the quoted Exec argument, then the Desktop Entry string layer.
    argument = ''.join('\\' + char if char in '\\"`$' else char
                       for char in str(launcher).replace('%', '%%'))
    return '"' + argument.replace('\\', '\\\\') + '"'


class Autostart:
    def __init__(self, config_home=None, launcher=None):
        root = config_home or os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config'
        self.path = Path(root) / 'autostart' / 'nekoinfo.desktop'
        self.launcher = launcher

    def _owned(self):
        try:
            return OWNER in self.path.read_text(encoding="utf-8").splitlines()
        except UnicodeError:
            return False

    def enabled(self):
        return self.path.is_file() and self._owned()

    def set_enabled(self, enabled):
        if self.path.exists() and not self._owned():
            raise FileExistsError('An unrelated nekoinfo.desktop already exists in autostart.')
        if not enabled:
            self.path.unlink(missing_ok=True)
            return
        launcher = self.launcher or shutil.which('nekoinfo')
        if not launcher:
            raise FileNotFoundError('Install the nekoinfo launcher before enabling login startup.')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        content = ('[Desktop Entry]\nType=Application\nName=Neko Info\n'
                   f'Exec={desktop_exec(launcher)}\nIcon=nekoinfo\nTerminal=false\n{OWNER}\n')
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', dir=self.path.parent, delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
