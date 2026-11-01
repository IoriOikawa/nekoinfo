# Validation and compatibility

[README](../README.md) · [Build/install](building.md) · [FAQ](faq.md)

This file separates automated/local evidence, user-reported Linux observations and checks still required before broader compatibility or performance claims. Updated 2026-11-01.

## Current evidence

| Check | Result | Scope |
| --- | --- | --- |
| Unit tests | 21 pass | Sampling/history, metric recovery, suspend detection, autostart ownership/quoting/errors, CLI renderer selection and theme adapter |
| Python compilation | Pass | src and tests |
| Wheel and sdist | Built and inspected | Single source package, launcher metadata, icon and desktop entry |
| Installed Python wheel | Native GTK smoke passed outside source tree | macOS only; does not validate Linux package placement |
| Native GTK smoke | Pass | macOS GTK 4.24 / PyGObject 3.58 / Python 3.14.3; drawing, live window/timer, expansion, denied login writes, zero-font theme and cleanup |
| Ubuntu installation and basic use | User reports success | Ubuntu 24.04.5 LTS x86_64, GNOME 46.0/Mutter, GTK 4.14.5+ds-0ubuntu0.10 |
| Screenshot | User-provided real window capture | ../screenshot_new.png; custom dark theme, processor details expanded |
| Independent review | Passed | App, renderer fix, local theme guard and documentation reviewed |
| Linux CI | Both package jobs passed | Debian stable and Arch containers; build, install, CLI/menu resources, installed Xvfb GTK smoke |

Development host: macOS arm64. Python 3.12.12 with psutil 7.2.2 is used for isolated unit/build checks. No Linux VM/container engine is installed locally. The temporary macOS GTK test runtime is not shipped with the application.

## Ubuntu field report

The user built/installed the package, opened the window and observed normal live refresh. Session type (X11/Wayland), Mesa version, scale factor and long-duration resource measurements have not been collected. The supplied screenshot confirms the native dark window and expanded per-core view; it is not a resource-use benchmark.

### Startup renderer

Initial launch took approximately 30 seconds and reported EGL/Mesa/ZINK initialization warnings. After closing the window and launching `GSK_RENDERER=cairo nekoinfo`, the user reported immediate display and no EGL/Mesa warnings. Two GtkImage baseline warnings remained.

This A/B comparison establishes an effective renderer workaround on that machine, not a diagnosis of a specific faulty driver. The Linux launcher now sets the Cairo default before GTK imports, preserving explicit renderer preferences. Terminal, menu and login launch paths use that launcher. The integrated default still needs confirmation after installing the updated build on the Ubuntu machine; the field comparison used an explicit environment variable.

### Theme baseline warning

User configuration: WM theme Adwaita, application theme reported as WhiteSur-Dark-grey [GTK2/3]. GTK4 also had gtk.css and gtk-dark.css linked to gtk-Dark.css. Both supplied dark/light theme files contained `switch { ... font-size: 0; ... }`; settings.ini only set gtk-application-prefer-dark-theme=0.

Observed comparisons:

1. Cairo + existing configuration: immediate startup; baseline warnings remain.
2. Cairo + GTK_THEME=Adwaita: warnings remain.
3. Cairo + Adwaita + fresh temporary XDG_CONFIG_HOME: no warnings.
4. Existing theme files with only switch font-size changed from 0 to 13px: user reports no warnings.

GTK 4.14.5 computes image baseline ratios from font ascent/descent; zero font metrics explain the observed failure mechanism. The single-rule theme correction was confirmed by the user. It does not establish that every WhiteSur version or GTK installation is affected.

For distribution, Neko Info instead marks its login switch and explicitly sets only its direct image children's font to 13px. The application's provider uses application priority, leaving user theme colors and geometry intact. This explicit child value overrides the problematic inherited parent value. No user configuration is rewritten, and warnings are not filtered.

The GTK smoke now injects a user-priority zero-font parent rule and verifies the marked images retain nonzero font metrics. This passes locally on GTK 4.24, where the original invalid baseline was not reproduced. The application-local guard still needs installation and confirmation on Ubuntu GTK 4.14.5, with an unmodified zero-font theme. Healthy light/dark themes and high-DPI appearance must also be checked.

## Linux CI

[Run 41322606447](https://github.com/IoriOikawa/nekoinfo/actions/runs/41322606447), commit 5933246, passed both Debian stable and Arch jobs on 2026-11-01. Both jobs built and installed their native packages, checked CLI version/desktop entry/icon and ran the installed GTK smoke, including the zero-font theme guard. Package artifacts were uploaded. This establishes Linux package and Xvfb coverage, not a real GNOME/KDE session or Ubuntu GTK 4.14 behavior.

Detailed Debian logs also exposed missing dh_python3 sequence integration and zero tests discovered inside the package build (the separate CI unit step did run all 21 tests). A follow-up enables the Python3 debhelper sequence, explicitly selects the source tests directory, and checks the built package has a Python interpreter dependency. Its fresh CI run must be checked before using its artifacts.

## Target matrix

| Environment | Package build/install | Window/live refresh | Theme/login/suspend/scaling/performance |
| --- | --- | --- | --- |
| Ubuntu 24.04.5, GNOME 46.0, GTK 4.14.5; session type unreported | User-reported success | User-reported success; screenshot supplied | Theme-file correction confirmed; app-local guard and remaining checks pending |
| Debian stable, GNOME Wayland | CI build/install passed | Desktop pending; installed Xvfb smoke passed | Pending |
| Debian stable, KDE Wayland | CI build/install passed | Desktop pending; installed Xvfb smoke passed | Pending |
| Arch Linux, GNOME Wayland | CI build/install passed | Desktop pending; installed Xvfb smoke passed | Pending |
| Arch Linux, KDE Wayland | CI build/install passed | Desktop pending; installed Xvfb smoke passed | Pending |
| Other X11 sessions | Pending | Pending | Pending |

A Debian/Arch container build and installed Xvfb smoke can validate packaging and GTK startup, but not GNOME/KDE Wayland behavior. Login execution requires an actual desktop session. No measured CPU/RSS budget is published yet.

## Reproduce automated checks

With dependencies installed as described in building.md:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall -q src tests
python3 -m build --no-isolation
PYTHONPATH=src xvfb-run -a dbus-run-session -- python3 tests/gtk_smoke.py
git diff --check
```

To test the installed Linux module, omit PYTHONPATH for the smoke. The smoke fails when dependencies/display are missing. Mac native smoke is supplementary and not a substitute for target validation.

## Desktop and release checklist

Record /etc/os-release, uname -a, Python/psutil/GTK versions, desktop version, session type, scaling and hardware with results.

- Build/install the package in a clean target distribution; verify launcher, desktop entry, icon, upgrade and uninstall. Check menu launch and repeated activation.
- Validate default renderer startup without an explicit environment variable on the reported Ubuntu machine.
- Test the application-local theme guard with the original zero-font switch rule. Check default light/dark themes, system preference changes, contrast, keyboard use and 100%/150%/200% display scaling.
- Expand processor details on a high-core machine; only that region should scroll, and collapse should restore the compact view.
- Compare CPU/memory/network with known load/counters. Disconnect/reconnect networking, add/remove a VPN, suspend/resume, and trigger an individual metric failure. Expect gaps/waiting instead of negative rates or resume spikes.
- Confirm login startup is initially off. Enable, log out/in and check one window; disable and repeat. Verify write-denied XDG directories produce a visible error and an unrelated autostart file is untouched.
- Run idle for 30 minutes; record process CPU time and RSS at 0/5/15/30 minutes using `ps -p PID -o pid,etime,time,rss`. State units and CPU-time calculation. Repeat with details expanded. History stays within 60 seconds/128 samples; require no sustained growth.
- Close the window and verify process exit/timer cleanup. Disable login startup before uninstalling; document the user-owned entry if left behind.
- Retain a current window screenshot and add a full desktop capture with resolution/scale for future layout comparison.
