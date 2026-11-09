# Systemd Service Manager v1.0.1

Maintenance and UI enhancement update focusing on seamless upgrade workflows and native aaPanel theme integration.

## What's New

- **Smart Installation & Update Handling (`install.sh`):**
  - Running `install.sh install` now automatically checks if the plugin is already installed. If present, it seamlessly performs an update to the latest release instead of failing or performing a blind re-install.
  - Added dedicated support for `install.sh update` (and `upgrade`).
  - Added fail-safe multi-tier update mechanisms: Git pull with safe directory configuration, GitHub archive (`main.zip`) download via `curl`/`wget` with `unzip` extraction, shallow git clone fallback, and local copy if executed from an updated clone.
  - Safe default: executing `bash install.sh` without arguments no longer falls through to uninstall.
- **Native aaPanel Theme Inheritance (Light & Dark Mode):**
  - Completely refactored plugin styling with CSS custom properties (`--sm-*`), inheriting aaPanel's `--layui-layer-bg` and panel background colors.
  - Native dark mode support adapting to aaPanel's `data-theme="dark"` attribute, dark body classes (`.dark`, `.theme-dark`, `.bt-dark`), and system `prefers-color-scheme`.
  - Added dynamic JavaScript `MutationObserver` on `<html>` and `<body>` to automatically sync theme state in real-time when toggled in the aaPanel header without reloading the page.
  - Full theme adaptation for all modal dialogues (`layer.open`): Status & Journal logs, Unit file editor, New service form, and Confirm delete dialogs.

---

# Systemd Service Manager v1.0.0

Initial release of Systemd Service Manager, an aaPanel plugin for managing systemd services on Linux servers.

## Features

- Browse system services and custom services, with status filters and search.
- Start, stop, and restart services.
- Enable or disable automatic startup at boot.
- View service status, process ID, memory usage, and recent journal logs.
- Create custom services with a quick form or a complete systemd unit file.
- Edit service unit files and optionally restart a service after saving.
- Delete custom services and reload the systemd daemon configuration.

## Requirements

- Linux with systemd (`systemctl`).
- aaPanel with administrative privileges.
- `journalctl` for viewing service logs.

## Installation

Clone the repository into the aaPanel plugin directory:

```bash
sudo git clone https://github.com/huynhngoanhthai/Systemd-Service-Manager-1.0.git \
  /www/server/panel/plugin/service_manager
```

Then run the included installation script:

```bash
sudo bash /www/server/panel/plugin/service_manager/install.sh install
```

The installation script creates the plugin directory if needed; it does not download or copy the plugin files. See [README.md](README.md) for details.

## Notes

- Service management actions can affect running applications and server availability.
- Deleting a custom service stops it, disables boot startup, and removes its unit file from `/etc/systemd/system/`.
- Logs are fetched when opened or refreshed; live log streaming is not included.
