# Validation record

## Verified on 2026-11-01

Development host: macOS arm64, Python 3.14.3; isolated build environment Python 3.12.12, psutil 7.2.2. No Linux VM/container engine is installed on this host.

- `PYTHONPATH=src python3 -m unittest discover -s tests -v`: 18 tests pass (CPU warm-up/averaging, memory semantics, network intervals/interface changes/resets/errors, suspend detection, bounded history, XDG default/ownership/quoting/errors CLI version and portal theme mapping/error/cleanup).
- `PYTHONPATH=src python3 -m compileall -q src tests`: bytecode compilation.
- Isolated `python -m build`: wheel and sdist, inspected for a single source package, launcher entry point, desktop file and icon.
- `git diff --check`: whitespace validation.
- Real psutil sampling without GTK: warm-up and later sample exercised.
- Installed the built wheel in an isolated Python 3.14 environment and ran the native GTK smoke from outside the repository, resolving the installed package rather than source. CLI `nekoinfo --version` returned 2.0.0.
- Visually inspected the actual macOS GTK window: current values and four curves render, processor details expand, and closing exits the process. This does not validate Linux appearance.
- Shell syntax checked for PKGBUILD and prepare-source.sh; tracked executable bits checked for debian/rules and prepare-source.sh.
- Independent design and code reviews approved the implementation; the older-GTK desktop appearance adapter was added in response to review.
- Native GTK smoke: task-local Homebrew GTK 4.24/PyGObject 3.58 runtime, Python 3.14.3, macOS display. `python3 <temporary-runtime>/run.py /tmp/nekoinfo-gtk-env/bin/python tests/gtk_smoke.py` sampled, drew all four charts, repeated activation, closed the window and verified removal of the GLib timer. This is not Linux compatibility evidence; the temporary runtime is not part of the application.

The GTK smoke intentionally fails when dependencies/display are absent. On Linux with distro dependencies, run `xvfb-run -a dbus-run-session -- python3 tests/gtk_smoke.py` after installing the package, or set `PYTHONPATH=src` to test source. CI config builds/installs Debian and Arch packages and runs this smoke against the installed package; CI execution is not yet verified.

## Pending target validation

### User-reported Ubuntu result

Ubuntu 24.04.5 LTS x86_64, GNOME 46.0 (user-reported; GTK/Mesa versions and session type not yet collected): package installation completed, `nekoinfo` eventually opens and refreshes normally. Startup takes approximately 30 seconds. Terminal output reports EGL/Mesa device initialization failures, including `ZINK: failed to choose pdev` and `egl failed to create dri2 screen`, followed by two GtkImage baseline warnings.

Follow-up comparison reported by the user: closing the existing window and launching `GSK_RENDERER=cairo nekoinfo` makes the window appear immediately, with no EGL/Mesa warnings. The two GtkImage baseline warnings remain. This isolates renderer selection as the effective startup workaround on this machine, but does not identify a specific faulty graphics driver. The Linux launcher now defaults to Cairo before GTK imports, while preserving an explicitly set `GSK_RENDERER`. No system settings are changed.

GtkImage baseline warnings are tracked separately: they persist without the startup delay, and their exact widget/GTK-version cause has not been reproduced locally. Do not hide warnings globally or claim they are fixed. Full GTK version, theme and a stack trace at the warning would be needed to locate their source.

Regression tests verify Linux default selection before GTK import, preservation of explicit renderer preferences, and unchanged defaults on other platforms. The full suite now contains 21 tests. The modified default still requires reinstallation and confirmation on the user's Ubuntu machine; the user comparison used the explicit environment variable on the previous build.

This report establishes installation and basic window/refresh behavior on one Ubuntu machine; it does not establish complete desktop compatibility, performance, or Debian/Arch package validation.

| Environment | Package build/install | Menu launch/window | Theme, scaling, login/suspend |
| --- | --- | --- | --- |
| Debian stable, GNOME Wayland | Pending | Pending | Pending |
| Debian stable, KDE Wayland | Pending | Pending | Pending |
| Arch Linux, GNOME Wayland | Pending | Pending | Pending |
| Arch Linux, KDE Wayland | Pending | Pending | Pending |
| X11 | Pending | Pending | Pending |

Record `/etc/os-release`, `uname -a`, Python/psutil/GTK versions, GNOME Shell or Plasma version, session type, display scaling and hardware alongside results. Container/Xvfb smoke does not validate GNOME/KDE or Wayland desktop behavior. Package commands and CI must still execute in clean Linux environments before package readiness is claimed.

## Repeatable desktop checks

1. Build/install a package using README commands. Confirm `nekoinfo --version`, menu launch, icon resolution, moving/resizing and ordinary-user launch. Launch twice and confirm one window/process/timer. Expand processors on a high-core system: only the details scroll; collapse returns to compact overview.
2. Change system light/dark theme and display scale (100%, 150%, 200%). Check all labels, curves, contrast, tooltips, window decorations and keyboard navigation. Capture a real window image and a full desktop image, recording resolution/scale; do not substitute the historical screenshot.
3. Compare CPU with a known load and per-core readings, memory with total/available, and transfer traffic with interface counters. Disconnect/reconnect networking, create/remove a VPN, and suspend/resume. Expect waiting/gaps rather than negative rates or a post-resume spike. Make one metric unavailable where possible and confirm other metrics continue.
4. Confirm login switch initially off and no autostart file. Enable it and log out/in: one window opens. Disable and log out/in: none opens. Check XDG_CONFIG_HOME override and write-denied directory behavior. No root service or background restart is expected.
5. Leave the window idle for 30 minutes. Record process CPU and RSS at 0, 5, 15 and 30 minutes using `ps -p PID -o pid,etime,time,rss`; state CPU calculation (CPU time difference divided by elapsed wall time) and RSS units. Record history length (at most 128 and 60 seconds) using an instrumented development session if needed. No performance budget is asserted until measured. Repeat with processor details expanded and confirm no sustained growth.
6. Close the window and confirm its PID is gone and no autostart/service launches it again. Upgrade and uninstall the package; confirm launcher/desktop/icon removal and document the user-owned autostart file behavior.
