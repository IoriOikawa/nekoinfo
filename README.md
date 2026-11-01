# Neko Info

A small native Linux desktop window for CPU, memory and network activity. Python 3.11+, GTK4, psutil and Cairo replace the old browser-based display. It samples every two seconds and keeps up to 60 seconds of in-memory trends. A static cat, system light/dark theme, scrollable logical-processor details and an opt-in **Start at login** switch keep the default view compact.

This is a source release under development, not an official Debian repository or AUR package. Debian stable and Arch Linux are the packaging targets. Linux desktop and package validation remains pending; see [testing status](docs/testing.md). No resource-use benchmark is claimed.

## Build and install

Use distribution packages for runtime dependencies; the application never runs pip or downloads dependencies on installation/startup.

Debian development/build environment:

```sh
sudo apt install build-essential debhelper dh-python pybuild-plugin-pyproject python3-all python3-setuptools python3-build python3-wheel python3-psutil python3-gi python3-gi-cairo python3-cairo gir1.2-gtk-4.0
# Run from this source directory:
dpkg-buildpackage -us -uc -b
sudo apt install ../nekoinfo_2.0.0_all.deb
nekoinfo
# Remove:
sudo apt remove nekoinfo
```

Arch development/build environment:

```sh
sudo pacman -S --needed base-devel python python-psutil python-gobject python-cairo gtk4 python-build python-installer python-setuptools python-wheel
# Generate a real local sdist and write its SHA-256 into PKGBUILD:
./packaging/arch/prepare-source.sh
cd packaging/arch
makepkg -si
# Remove:
sudo pacman -R nekoinfo
```

The Arch recipe uses the archive beside PKGBUILD, not a fictitious release URL. Regenerate the archive and checksum after source changes. The recorded checksum documents a generated local archive; generated archives are not tracked. Build as an ordinary user.

Debian maintainer metadata uses an explicit local-build placeholder address; replace it before a public package release. Original author Cocoa Oikawa and MIT attribution remain in the source.

Both packages install the same `nekoinfo` launcher, application-menu entry and `hicolor` icon. No root service runs in the background. Close the window to exit. Repeated launches in one desktop session present the existing window.

For source development with distro runtime dependencies installed:

```sh
PYTHONPATH=src python3 -m nekoinfo
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 -m build
```

`nekoinfo --version` (or `PYTHONPATH=src python3 -m nekoinfo --version`) works without GTK. A missing GUI dependency produces a short installation diagnostic. GTK/GI are supplied by the distribution rather than automatically installed from PyPI.

## Reading the numbers

CPU is the mean of the logical processors sampled in one nonblocking interval. CPU and network wait for an initial baseline. Memory used means **total − available**; available includes reclaimable caches and is not simply free RAM. Swap is outside this overview.

Download and upload aggregate non-loopback network interfaces using counter differences divided by the actual monotonic elapsed time. VPNs, bridges and virtual interfaces can count traffic twice; this is not exact Internet bandwidth. Interface changes, decreasing counters, errors and long/resume gaps reset the baseline. Missing metrics do not stop other readings. Curves use actual timestamps, show only collected data and leave gaps for unavailable readings. History is bounded to 60 seconds and 128 samples, never saved to disk.

**Start at login** defaults off. Enabling writes only an application-owned `$XDG_CONFIG_HOME/autostart/nekoinfo.desktop` (default `~/.config/autostart/`). Disable it before uninstalling, or remove that file yourself afterward. An unrelated file at that path is left untouched and an error is shown. This setting launches at desktop login, not system boot.

This is a normal movable/closable window. Desktop pinning, process management, GPU/temperature/disk metrics, remote monitoring and animated mascots are outside this version. It follows desktop font/theme settings; the old HTML-path/window-position configuration is not migrated.

The existing `screenshot.jpg` shows the **historical browser-based version**, not this release. No new desktop screenshot or performance figure is supplied until captured on the target Linux desktop. MIT license and original artwork/author attribution are preserved.
