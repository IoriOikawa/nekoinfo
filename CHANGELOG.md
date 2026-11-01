# Changelog

## 2.0.0 — development

- Replace the 2017 GTK3/WebKit display with Python/GTK4 native controls and Cairo trends.
- Show CPU, available-memory-based RAM usage, network rates and expandable per-core details.
- Sample every two seconds and bound history to 60 seconds/128 samples; reset CPU/network baselines after discontinuities.
- Add opt-in, user-owned desktop login startup with write-error handling.
- Follow desktop appearance preferences, with an asynchronous portal bridge for older GTK.
- Default Linux launches to Cairo after a user-confirmed EGL/Mesa startup-delay workaround; preserve explicit renderer choices.
- Give only the application's login-switch images a nonzero font to protect GTK4 baseline calculation from zero-font theme rules.
- Provide Debian/Ubuntu source packaging, an Arch local-source PKGBUILD and Linux build/smoke CI configuration.
- Add the user-provided Ubuntu screenshot, Chinese README, installation guide, FAQ and explicit validation matrix.

Ubuntu installation/window refresh and the theme-file correction have been reported successful by the user. The application-local theme guard and other desktop/distribution combinations still need the validation listed in [testing.md](docs/testing.md).

## 1.0 — historical (2017)

Tiny Ubuntu GTK desktop display using WebKit-rendered CPU and memory information. The original MIT author and icon attribution are retained.
