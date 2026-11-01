# Validation record

## Verified on 2026-11-01

Development host: macOS arm64, Python 3.14.3; isolated build environment Python 3.12.12, psutil 7.2.2. No Linux VM/container engine is installed on this host.

- `PYTHONPATH=src python3 -m unittest discover -s tests -v`: 18 tests pass (CPU warm-up/averaging, memory semantics, network intervals/interface changes/resets/errors, suspend detection, bounded history, XDG default/ownership/quoting/errors CLI version and portal theme mapping/error/cleanup).
- `PYTHONPATH=src python3 -m compileall -q src tests`: bytecode compilation.
- Isolated `python -m build`: wheel and sdist, inspected for a single source package, launcher entry point, desktop file and icon.
- `git diff --check`: whitespace validation.
- Real psutil sampling without GTK: warm-up and later sample exercised.
- Native GTK smoke: task-local Homebrew GTK 4.24/PyGObject 3.58 runtime, Python 3.14.3, macOS display. `python3 <temporary-runtime>/run.py /tmp/nekoinfo-gtk-env/bin/python tests/gtk_smoke.py` sampled, drew all four charts, repeated activation, closed the window and verified removal of the GLib timer. This is not Linux compatibility evidence; the temporary runtime is not part of the application.

The GTK smoke intentionally fails when dependencies/display are absent. On Linux with distro dependencies, run `xvfb-run -a dbus-run-session -- python3 tests/gtk_smoke.py` after installing the package, or set `PYTHONPATH=src` to test source. CI config builds/installs Debian and Arch packages and runs this smoke against the installed package; CI execution is not yet verified.

## Pending target validation

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
