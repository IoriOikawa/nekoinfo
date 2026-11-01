# Lightweight desktop implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Deliver the approved lightweight CPU, memory and network desktop application, with Debian and Arch source packaging.

**Architecture:** A single Python package holds independent sampling/history logic and a GTK4 application. One GLib timer updates existing widgets and bounded time-based graphs; no WebKit, subprocess polling or telemetry. Both distributions install the same source and desktop resources.

**Tech Stack:** Python >=3.11, psutil, PyGObject/GTK4, pycairo, setuptools, unittest, Debian debhelper/pybuild and Arch makepkg.

Design: `docs/superpowers/specs/2026-11-01-lightweight-desktop-design.md`.

## File responsibilities

- `src/nekoinfo/metrics.py`: timestamped immutable samples, CPU warm-up, isolated error handling, network deltas, bounded history.
- `src/nekoinfo/app.py`: GTK application/window, overview, per-core expander, one timer and cleanup.
- `src/nekoinfo/charts.py`: timestamp-based GTK DrawingArea trends, gaps and empty states.
- `src/nekoinfo/autostart.py`: opt-in XDG desktop autostart management; no service.
- `src/nekoinfo/__init__.py`, `__main__.py`: version and launch path with helpful missing-dependency errors.
- `pyproject.toml`: build metadata, console entry and shared resources.
- `data/nekoinfo.desktop`, `data/nekoinfo.svg`: application integration; reuse existing icon artwork.
- `tests/test_metrics.py`, `tests/test_autostart.py`: behavior tests with controlled metric providers and clocks, no GTK dependency.
- `debian/*`: native Debian source package, distro-managed runtime and build dependencies.
- `packaging/arch/PKGBUILD`: build same release source, no network during package install.
- `.github/workflows/ci.yml`: headless Linux GTK smoke test, Debian build and Arch clean build if feasible.
- `README.md`, `docs/testing.md`: installation, semantics, compatibility matrix and reproducible manual verification.
- Remove `DEBIAN/`, `usr/`, and legacy root `nekoinfo` after migration; preserve historical screenshot as explicitly historical until a genuine new capture exists.

## Task 1: sampler and bounded history

- [x] Add unittest cases first, using a controlled provider and explicit timestamps. Run `python3 -m unittest discover -s tests -v` and confirm missing implementation fails.
- [x] Define sample attributes `timestamp`, `cpu_percent`, `per_cpu`, `memory`, `network` with explicit unavailable values, then implement to satisfy tests.
- [x] Verify CPU warm-up, logical-core averaging, available-memory semantics, interface add/remove/reset, actual elapsed time, >10 second gaps and per-metric read failures. Failed network reads reset baseline; failed CPU reads force warm-up before reuse.
- [x] Use 60 second timestamp eviction and a defensive sample cap; unit-test both history bounds and graph gap representation.
- [x] Run tests to green. Exercise real psutil without importing GTK.

## Task 2: opt-in autostart

- [x] Test absent/default-off state, enabling, disabling, XDG_CONFIG_HOME and launch paths containing spaces. Use temporary directories; never change developer login settings.
- [x] Implement atomic app-owned desktop file updates, never overwrite unrelated files. Startup command must use a valid Desktop Entry Exec string with a stable installed launcher.
- [x] Run tests and confirm disabled state leaves no app-owned autostart file.

## Task 3: native GTK window

- [x] Build CPU, memory and up/down network rows with labelled 60 second curves. Initial CPU/network show waiting; read failures show unavailable. Use reusable Cairo DrawingAreas, explicit units and bounded scales.
- [x] Add scrollable per-core expander, system-following light/dark styling, static cat brand, default-off login switch. Explain memory and network semantics through visible help/tooltips.
- [x] Register exactly one two-second timer on activation; repeated activation presents the existing window. On close remove the timer and exit cleanly. Detect resume gaps via clocks and reset baselines/history discontinuities.
- [x] Provide graceful CLI dependency diagnostics, `--version` without GTK, and a Linux headless smoke mode/test that samples, draws, closes and checks timer cleanup. Do not silently skip available Linux runtime failures.

## Task 4: one build and two distro packages

- [x] Add standard project metadata and data-files; build with `python3 -m build` in a temporary development environment. Inspect wheel and sdist for required files and absence of legacy duplication.
- [x] Debian: use debhelper, dh-python, pybuild and setuptools; runtime deps include python3-psutil, python3-gi, python3-gi-cairo, python3-cairo and gir1.2-gtk-4.0. Validate source structure. Linux execution of `dpkg-buildpackage -us -uc -b` remains pending in the matrix below.
- [x] Arch: declare python, python-psutil, python-gobject, python-cairo, gtk4; build with python-build/python-installer/python-setuptools/python-wheel. Use an actual local release archive and checksum, with documented creation and `makepkg` instructions; do not invent a published URL/tag.
- [x] Add CI jobs using Debian stable and Arch containers with Xvfb, GTK smoke verification and package artifacts. Validate command paths from built packages, including desktop icon resolution.
- [x] Remove legacy executable and packaged tree only after standard build includes replacements.

## Task 5: validation and delivery

- [x] Update README with actual build/install/uninstall commands, supported Python, CLI launch, autostart, data semantics and honest compatibility status. Document GNOME/KDE Wayland matrix as pending unless actually exercised.
- [x] Run unit tests, compile checks, wheel/sdist build and whitespace checks. Run GTK smoke where dependencies/display are available. Record exact commands, counts and limitations in `docs/testing.md`.
- [x] Add repeatable 30-minute memory/CPU and login/suspend/network/high-DPI manual verification instructions. No unmeasured resource claims or fabricated screenshots.
- [x] Request independent spec review, resolve required findings, then independent quality review and resolve required findings. Update this checklist with evidence.
- [x] Commit implementation on `codex/lightweight-desktop`. Make the reviewed branch available in the user's original workspace, keeping master history intact and retaining any unverified Linux checks explicitly.

## Implementation evidence (2026-11-01)

Initial implementation: 18 unittests passed on macOS Python 3.14.3; Python 3.12.12 wheel/sdist build and archive inspection pass. Real psutil sampling and native macOS GTK4.24 smoke pass (single window/timer, all Cairo charts, scrollable expander minimum, close cleanup). Debian/Arch build and installed Linux smoke remain pending; CI is configured, not executed. GNOME/KDE Wayland, 30-minute performance/login/suspend manual checks remain pending in docs/testing.md. Parent coordinates independent review and final branch delivery.

## Delivery evidence

- Implemented and independently reviewed; Initial implementation: 18 unit tests passed on Python 3.12 and native GTK smoke passes on macOS/Python 3.14.
- Installed wheel tested from outside the source tree: CLI version, sampling, drawing, window reuse and cleanup pass.
- Wheel/sdist build, packaged resources, shell syntax and whitespace checks pass.
- Spec and code quality reviewers approved after fixing the Debian GTK4.18 dark-preference gap.
- [x] Execute Debian and Arch package builds/installations in Linux CI (run 41322606447; desktop sessions remain separate).
- [ ] Validate GNOME/KDE Wayland, real login/suspend/high-DPI behavior and capture Linux screenshots.
- [ ] Measure 30-minute resource usage on Linux before setting a numeric performance budget.

These pending checks are release validation requirements; they are not claimed complete.

## Follow-up delivery (2026-11-01)

- [x] Rename the local development branch to dev at the user's request.
- [x] Apply Linux Cairo default after a user A/B startup comparison, with three CLI regression tests (21 unit tests total).
- [x] Add application-scoped nonzero switch-image font guard after the user confirmed the theme's zero-font trigger. Watch the GTK smoke fail before implementation and pass afterward.
- [x] Rewrite English/Chinese README, build/install guide, FAQ, changelog and validation record around the supplied screenshot_new.png and actual field results.
- [ ] Confirm the application-local theme guard on Ubuntu with the original unmodified theme.
- [x] Push dev and inspect Debian/Arch CI run 41322606447: both package jobs passed. Detailed logs prompted a follow-up Python dependency/test-discovery packaging correction, to be rechecked in CI.

The current validation source of truth is docs/testing.md; the earlier evidence sections describe the initial implementation checkpoint.
