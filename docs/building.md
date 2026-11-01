# Build, install and develop

[README](../README.md) · [简体中文](../README.zh-CN.md) · [FAQ](faq.md) · [Validation](testing.md)

Neko Info 2.0.0 uses Python 3.11+, GTK4, PyGObject/GI Cairo, pycairo and psutil. Install dependencies with the distribution package manager. The first dependency installation needs Internet access unless packages are already available locally.

## Get the source

Use a clone of the development branch:

```sh
git clone --branch dev https://github.com/IoriOikawa/nekoinfo.git
cd nekoinfo
```

A USB copy of the checked-out project also works. Copy it to a writable local folder on the Linux machine before building. Git branches are versions of the same working directory, not separate folders; a copy made while dev is checked out contains dev's files. The .git directory is optional for building, and Mac virtual environments/build caches are not needed.

Build as an ordinary user. Use sudo only for package-manager operations. Never copy a macOS virtual environment into the Linux runtime.

## Debian and Ubuntu

Ubuntu 24.04 provides a sufficiently recent system Python. Check `python3 --version` on other releases: this project requires 3.11 or later; do not replace the distribution's system Python to satisfy the requirement.

```sh
sudo apt update
sudo apt install build-essential debhelper dh-python pybuild-plugin-pyproject python3-all python3-setuptools python3-build python3-wheel python3-psutil python3-gi python3-gi-cairo python3-cairo gir1.2-gtk-4.0
```

On Ubuntu, pybuild-plugin-pyproject is in Universe; if apt cannot locate it, enable that repository using Software & Updates, refresh the package lists, and retry.

From the project root:

```sh
dpkg-buildpackage -us -uc -b
sudo apt install ../nekoinfo_2.0.0_all.deb
nekoinfo
```

If a USB filesystem lost executable permissions, restore `chmod +x debian/rules` before building.

For an updated development build with the same version number, close the old window, rebuild, then explicitly reinstall:

```sh
sudo apt install --reinstall ../nekoinfo_2.0.0_all.deb
```

Remove with `sudo apt remove nekoinfo`. Disable **Start at login** before uninstalling, or remove the app-owned autostart entry afterward as described in the FAQ.

The Debian maintainer address is deliberately an example.invalid local-build placeholder. Set correct public maintainer metadata before publishing a distribution package. Ubuntu user installation does not establish Debian stable validation.

## Arch Linux

```sh
sudo pacman -Syu --needed base-devel python python-psutil python-gobject python-cairo gtk4 python-build python-installer python-setuptools python-wheel
./packaging/arch/prepare-source.sh
cd packaging/arch
makepkg -si
nekoinfo
```

Run prepare-source.sh from the repository and makepkg as an ordinary user. The helper creates a real local source archive beside PKGBUILD and records its SHA-256; regenerate it after changing source or documentation. The recipe intentionally does not refer to an unpublished release URL. Generated archives/build outputs are ignored by Git and excluded from subsequent sdists.

Remove with `sudo pacman -R nekoinfo`, after disabling login startup. This recipe has not been published to AUR, and its container build/install/installed-GTK smoke passed in CI; real desktop checks remain pending.

## Source development

With distro runtime dependencies installed:

```sh
PYTHONPATH=src python3 -m nekoinfo
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall -q src tests
python3 -m build --no-isolation
```

Python build/setuptools/wheel must be installed before --no-isolation. Runtime GI/GTK packages come from the distribution, not from automatic PyPI installation. `python3 -m build` can use an isolated build environment when that is preferred and network access is available.

`PYTHONPATH=src python3 -m nekoinfo --version` works without importing GTK. Source launch does not install an application-menu entry or a stable login launcher; use the distro package to test that integration.

## GTK smoke and CI

On Debian/Ubuntu install `xvfb xauth dbus-x11`; on Arch install `xorg-server-xvfb xorg-xauth dbus`. Then:

```sh
PYTHONPATH=src xvfb-run -a dbus-run-session -- python3 tests/gtk_smoke.py
```

After package installation, omit PYTHONPATH to test the installed module rather than source. The smoke covers drawing, one live window/timer, processor expansion, a zero-font switch theme, denied login writes and cleanup. Missing GTK/display dependencies are failures, not silently skipped tests.

[GitHub Actions](../.github/workflows/ci.yml) defines Debian stable and Arch container builds, package installation and installed GTK smoke checks, with downloadable package artifacts when successful. Container/Xvfb success does not establish GNOME/KDE Wayland behavior. The first pushed run passed both jobs; see [recorded evidence](testing.md#linux-ci). Check the actual run results for the commit you use. Debian-built .deb artifacts are tested on Debian stable; Ubuntu users should build locally until that exact artifact has been verified on their Ubuntu release.

## Contributing

Keep the default view compact and introduce no polling subprocesses, browser runtime, telemetry or unbounded history. Put sampling/rate/history regression tests in tests/test_metrics.py; launch environment tests in tests/test_cli.py; GTK integration checks in tests/gtk_smoke.py.

A bug report should include distro, desktop/session type, GTK version, complete terminal output and reproduction steps. For theme issues include a minimal relevant CSS rule, not your entire home directory. See [testing.md](testing.md) for manual checks and [CHANGELOG.md](../CHANGELOG.md) for current changes.
