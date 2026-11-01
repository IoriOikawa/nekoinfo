# Frequently asked questions

[README](../README.md) · [简体中文](../README.zh-CN.md) · [Build/install](building.md) · [Validation](testing.md)

## Slow startup or EGL/Mesa warnings

One Ubuntu 24.04.5 / GNOME 46.0 machine took about 30 seconds to show the window and reported EGL/Mesa/ZINK initialization failures. With `GSK_RENDERER=cairo nekoinfo`, the user reported immediate startup and no EGL/Mesa warnings.

The Linux launcher now defaults to Cairo before GTK imports. This process-local setting is used for terminal, application-menu and login launches. It preserves an explicit GSK_RENDERER choice and does not change drivers or system configuration. Software rendering still requires resource measurements; it is not necessarily lower-CPU than GPU rendering.

Close any existing window before comparing launch behavior; otherwise single-instance activation can present the old process. If an older build is installed, try:

```sh
GSK_RENDERER=cairo nekoinfo
```

To experiment with the normal GTK renderer selection, an explicitly empty value leaves selection to GTK; an explicit supported renderer such as `GSK_RENDERER=gl nekoinfo` also overrides the application default. Availability depends on the installed GTK/backend. See [GTK renderer documentation](https://docs.gtk.org/gtk4/running.html#gsk_renderer).

## GtkImage baseline warnings

A warning such as `reported baselines of minimum -2147483648` was reproduced by a user with GTK 4.14.5 and a custom GTK4 theme. The theme had `switch { font-size: 0; }`. GtkSwitch contains two internal images, and GTK 4.14 computes their baselines from font ascent/descent. The user confirmed that changing the switch font to a nonzero size removed the warnings.

Current Neko Info marks its login switch with a dedicated CSS class and gives only its direct image children a 13px font. It retains theme colors and slider sizes. There is no theme-name detection, theme blacklist, global warning filter, or theme-file rewrite. The local zero-font regression smoke passes; the new application-local handling still needs confirmation on the user's Ubuntu GTK 4.14 installation.

Older installations should [rebuild/reinstall](building.md#debian-and-ubuntu) before editing any theme. If warnings remain, close the window and compare:

```sh
GSK_RENDERER=cairo GTK_THEME=Adwaita nekoinfo
```

GTK_THEME selects a theme but does not isolate user GTK4 CSS. To test a fresh config directory without moving or deleting the existing one:

```sh
neko_test_config=$(mktemp -d)
GSK_RENDERER=cairo GTK_THEME=Adwaita XDG_CONFIG_HOME="$neko_test_config" nekoinfo
```

This test also isolates other XDG configuration, including the login entry. Do not enable login startup during diagnosis. If only the clean-config test removes warnings, inspect ~/.config/gtk-4.0/ (or the configured XDG_CONFIG_HOME) for gtk.css, imports, links and settings.ini. Back up files before editing them. Fixing a theme for all GTK4 apps is a separate user choice; package installation never does it automatically.

Reference: [GTK 4.14.5 image baseline implementation](https://github.com/GNOME/gtk/blob/4.14.5/gtk/gtkimage.c#L908).

## Understanding the readings

**CPU:** average of the logical processors from a nonblocking sampling interval. The first reading waits for a baseline. Expand Logical processors for individual values.

**Memory:** used = total − available. Available includes reclaimable cache, so it differs from completely free RAM. Swap is not included in this overview. Sizes use binary GiB units.

**Network:** receive/send counter differences divided by actual monotonic elapsed time, displayed as KiB/s or MiB/s. All non-loopback interfaces are aggregated. VPNs, bridges and virtual interfaces can duplicate traffic; this value is not exact Internet bandwidth.

CPU/network readings reset after long gaps or detected suspend/resume; network also resets after interface changes, counter decreases and read failures. A missing metric does not stop the others. Trends contain only collected samples, keep at most 60 seconds/128 samples and are not saved to disk.

## Start at login

This option starts Neko Info at graphical desktop login, not at system boot. It is off by default and requires the installed nekoinfo launcher to be available.

It creates an application-owned file at `$XDG_CONFIG_HOME/autostart/nekoinfo.desktop`, defaulting to `~/.config/autostart/nekoinfo.desktop`. An unrelated existing file is left untouched and a write failure is displayed in the window. There is no root service or external daemon.

Disable the switch before uninstalling. If already uninstalled, remove only the Neko Info entry you enabled. In a graphical file manager, open ~/.config/autostart/ using the location bar (Ctrl+L on GNOME Files) and inspect nekoinfo.desktop first. User-owned login entries are not deleted by the system package manager.

## Can I pin it to the desktop?

This version is a normal window. Exact positioning, always-below behavior, hiding taskbar entries and cross-workspace pinning vary by compositor and are not promised. Desktop integration for GNOME/KDE is a future, separately scoped feature.

## Will it work offline or from a USB drive?

The installed application runs locally without network services. Initial dependency installation needs Internet access unless all distribution packages are already available offline. Copy source from USB to a writable local folder before building. Copy the checked-out dev working directory; there is no separate dev folder to locate. Detailed steps are in [building.md](building.md#get-the-source).

## Why is the old screenshot different?

[screenshot_new.png](../screenshot_new.png) is the current user-provided Ubuntu capture. [screenshot.jpg](../screenshot.jpg) is retained as the historical 2017 WebKit version. The current implementation uses native GTK widgets and Cairo trends.
