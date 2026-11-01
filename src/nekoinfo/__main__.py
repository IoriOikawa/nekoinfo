import argparse
import sys
from . import __version__


def main():
    parser = argparse.ArgumentParser(description='Neko Info native desktop system monitor')
    parser.add_argument('--version', action='version', version=f'Neko Info {__version__}')
    parser.parse_args()
    try:
        import gi
        gi.require_version('Gtk', '4.0')
        gi.require_foreign('cairo')
        import cairo
        import psutil
        from .app import NekoApplication
    except (ImportError, ValueError) as error:
        print(f'Neko Info needs GTK4, PyGObject, GI Cairo, pycairo and psutil: {error}\n'
              'Install the Neko Info distro package, or see README development dependencies.', file=sys.stderr)
        return 1
    return NekoApplication().run([sys.argv[0]])


if __name__ == '__main__':
    raise SystemExit(main())
