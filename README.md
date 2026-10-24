# Systemd Service Manager

An aaPanel plugin for managing systemd services on Linux servers through the aaPanel interface.

[Tiếng Việt](README_VI.md)

## Features

- List services and view running, stopped, failed, and boot auto-start states.
- Search and filter services by status, or view custom services separately.
- Start, stop, and restart services; enable or disable them at boot.
- View service status, PID, memory usage, and recent journal log lines.
- Create custom services with a quick form or by entering a complete systemd unit file.
- View and edit unit files, with an option to restart the service after saving.
- Delete custom services and reload the systemd configuration.

> Logs are loaded when the log window is opened or refreshed; continuous live streaming is not currently provided.

## Requirements

- A Linux server running `systemd` (`systemctl`).
- aaPanel installed.
- aaPanel running with administrative/root privileges to manage services and files under `/etc/systemd/system/`.
- `journalctl` for viewing logs.

This is an aaPanel plugin, not a standalone application, and it is not intended for Windows.

## Installation

### Option 1: Clone the repository

```bash
sudo git clone https://github.com/huynhngoanhthai/Systemd-Service-Manager-1.0.git \
  /www/server/panel/plugin/service_manager
```

Run the installation script:

```bash
sudo bash /www/server/panel/plugin/service_manager/install.sh install
```

### Option 2: Quick installation from a ZIP archive

Connect to the aaPanel server over SSH, then run the following block with an account that has `sudo` privileges. It downloads the latest source from the `main` branch, copies the plugin files into the correct directory, and runs the installation script:

```bash
sudo bash -c '
set -e
tmp_dir=$(mktemp -d)
trap "rm -rf \"$tmp_dir\"" EXIT
wget -q -O "$tmp_dir/service_manager.zip" "https://github.com/huynhngoanhthai/Systemd-Service-Manager-1.0/archive/refs/heads/main.zip"
unzip -q "$tmp_dir/service_manager.zip" -d "$tmp_dir"
install -d /www/server/panel/plugin/service_manager
cp -a "$tmp_dir/Systemd-Service-Manager-1.0-main/." /www/server/panel/plugin/service_manager/
bash /www/server/panel/plugin/service_manager/install.sh install
'
```

The server needs `wget` and `unzip`. The current `install.sh` only ensures that the plugin directory exists; the command above copies the source files there before running it. After installation, reload aaPanel and open the plugin if your aaPanel version/setup supports loading plugins from this directory.

The Python source syntax has been checked. The installation script is invoked with `bash`, so it does not need a separate executable permission.

## Usage

1. Open **Systemd Service Manager** in aaPanel.
2. Choose **Custom Services** or **All System Services**; use search and filters to find a service.
3. Use the actions beside a service to control it or view its logs.
4. Select **Add New Service** to create one. The quick form requires a service name and an `ExecStart` command; user, working directory, restart settings, and environment variables can also be configured.
5. Select **Raw Unit File** to enter a complete systemd unit file instead.

### Safety notes

- Service changes can interrupt applications or the server. Review unit files and commands before saving or restarting.
- Deleting a custom service stops it, disables boot auto-start, and removes its unit file from `/etc/systemd/system/` (including its `.bak` backup, if present). This cannot be undone from the plugin.
- The plugin runs system commands with the aaPanel process's privileges. Only install and use it on servers you administer.

## License

[MIT License](LICENSE)
