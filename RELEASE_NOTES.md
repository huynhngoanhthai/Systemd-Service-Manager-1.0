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
