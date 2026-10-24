# coding: utf-8
# +-------------------------------------------------------------------
# | aaPanel Systemd Service Manager Plugin
# +-------------------------------------------------------------------
# | Visual Systemd Service (systemctl) Manager on aaPanel GUI
# +-------------------------------------------------------------------

import os
import sys
import re
import json
import time
import shutil
import subprocess

try:
    import public
except ImportError:
    sys.path.insert(0, '/www/server/panel/class')
    import public


class service_manager_main:
    __plugin_name = 'service_manager'
    __setup_path = '/www/server/panel/plugin/' + __plugin_name
    __systemd_custom_path = '/etc/systemd/system'

    def __init__(self):
        pass

    def _clean_name(self, name):
        """Sanitize service name to prevent command injection"""
        if not name:
            return ''
        name = str(name).strip()
        # Remove quotes or leading/trailing spaces
        name = name.strip('\'"')
        if not re.match(r'^[a-zA-Z0-9_\-\.\@]+$', name):
            return ''
        return name

    def _ensure_service_suffix(self, name):
        name = self._clean_name(name)
        if not name:
            return ''
        if not name.endswith('.service'):
            name += '.service'
        return name

    def _run_cmd(self, cmd_list, timeout=20):
        """Execute command safely without shell=True where possible"""
        try:
            p = subprocess.run(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            return p.returncode, p.stdout.strip(), p.stderr.strip()
        except subprocess.TimeoutExpired:
            return -1, '', 'Command execution timed out'
        except Exception as e:
            return -1, '', str(e)

    def _format_memory(self, mem_bytes):
        try:
            b = int(mem_bytes)
            if b <= 0 or b >= 18446744073709551615:
                return '-'
            if b < 1024:
                return f"{b} B"
            elif b < 1024 * 1024:
                return f"{b / 1024:.1f} KB"
            elif b < 1024 * 1024 * 1024:
                return f"{b / (1024 * 1024):.1f} MB"
            else:
                return f"{b / (1024 * 1024 * 1024):.2f} GB"
        except:
            return '-'

    def get_service_list(self, get):
        """
        Retrieve systemd services list and overview statistics
        """
        try:
            # 1. Fetch loaded units
            _, out_units, _ = self._run_cmd(['systemctl', 'list-units', '--type=service', '--all', '--no-legend', '--no-pager'])
            # 2. Fetch unit files and boot state (enabled/disabled/static/masked)
            _, out_files, _ = self._run_cmd(['systemctl', 'list-unit-files', '--type=service', '--no-legend', '--no-pager'])

            unit_files = {}
            for line in out_files.splitlines():
                parts = line.strip().split()
                if len(parts) >= 2:
                    unit_files[parts[0]] = parts[1]

            services = {}
            for line in out_units.splitlines():
                line = line.strip()
                if line.startswith('●'):
                    line = line[1:].strip()
                parts = line.split(None, 4)
                if len(parts) >= 4 and parts[0].endswith('.service'):
                    name = parts[0]
                    services[name] = {
                        'name': name,
                        'load': parts[1],
                        'active': parts[2],
                        'sub': parts[3],
                        'desc': parts[4] if len(parts) > 4 else '',
                        'unit_file_state': unit_files.get(name, 'unknown'),
                        'is_custom': False
                    }

            for name, state in unit_files.items():
                if name not in services:
                    services[name] = {
                        'name': name,
                        'load': 'unloaded',
                        'active': 'inactive',
                        'sub': 'dead',
                        'desc': '',
                        'unit_file_state': state,
                        'is_custom': False
                    }

            # 3. Scan custom services in /etc/systemd/system
            if os.path.exists(self.__systemd_custom_path):
                for f in os.listdir(self.__systemd_custom_path):
                    f_path = os.path.join(self.__systemd_custom_path, f)
                    if f.endswith('.service') and not os.path.islink(f_path):
                        if f in services:
                            services[f]['is_custom'] = True
                        else:
                            services[f] = {
                                'name': f,
                                'load': 'loaded',
                                'active': 'inactive',
                                'sub': 'dead',
                                'desc': '',
                                'unit_file_state': unit_files.get(f, 'disabled'),
                                'is_custom': True
                            }

            # Overview statistics
            total = len(services)
            running_count = 0
            stopped_count = 0
            failed_count = 0
            custom_count = 0
            enabled_count = 0

            for s in services.values():
                act = s.get('active')
                sub = s.get('sub')
                ufs = s.get('unit_file_state')
                if act == 'active' and sub == 'running':
                    running_count += 1
                elif act == 'failed' or sub == 'failed':
                    failed_count += 1
                else:
                    stopped_count += 1

                if s.get('is_custom'):
                    custom_count += 1
                if ufs == 'enabled':
                    enabled_count += 1

            stats = {
                'total': total,
                'running': running_count,
                'stopped': stopped_count,
                'failed': failed_count,
                'custom': custom_count,
                'enabled': enabled_count
            }

            # Filter by search & filter_type
            filter_type = getattr(get, 'filter_type', 'all')
            search_str = getattr(get, 'search', '').strip().lower()

            service_list = list(services.values())

            # Priority: Custom first, then active/running, then alphabetical A-Z
            def sort_key(x):
                is_c = 0 if x.get('is_custom') else 1
                is_r = 0 if (x.get('active') == 'active' and x.get('sub') == 'running') else 1
                is_f = 0 if (x.get('active') == 'failed' or x.get('sub') == 'failed') else 1
                return (is_c, is_f, is_r, x.get('name').lower())

            service_list.sort(key=sort_key)

            filtered = []
            for s in service_list:
                # Filter by status
                if filter_type == 'running':
                    if not (s['active'] == 'active' and s['sub'] == 'running'):
                        continue
                elif filter_type == 'stopped':
                    if s['active'] == 'active' and s['sub'] == 'running':
                        continue
                    if s['active'] == 'failed' or s['sub'] == 'failed':
                        continue
                elif filter_type == 'failed':
                    if not (s['active'] == 'failed' or s['sub'] == 'failed'):
                        continue
                elif filter_type == 'custom':
                    if not s['is_custom']:
                        continue
                elif filter_type == 'enabled':
                    if s['unit_file_state'] != 'enabled':
                        continue

                # Filter by search string
                if search_str:
                    if (search_str not in s['name'].lower()) and (search_str not in s['desc'].lower()):
                        continue

                filtered.append(s)

            # Pagination
            try:
                page = int(getattr(get, 'p', 1))
            except:
                page = 1
            try:
                limit = int(getattr(get, 'row', 50))
            except:
                limit = 50

            filtered_total = len(filtered)
            if limit > 0:
                start = (page - 1) * limit
                end = start + limit
                page_data = filtered[start:end]
            else:
                page_data = filtered

            return {
                'status': True,
                'data': page_data,
                'total': filtered_total,
                'page': page,
                'limit': limit,
                'stats': stats
            }
        except Exception as e:
            return public.returnMsg(False, 'Failed to fetch service list: ' + str(e))

    def service_action(self, get):
        """
        Execute actions: start, stop, restart, reload, enable, disable, mask, unmask, reset-failed
        """
        name = self._ensure_service_suffix(getattr(get, 'service_name', ''))
        # Use 'act' first to avoid overriding aaPanel's reserved query parameter 'action=a'
        action = str(getattr(get, 'act', getattr(get, 'action', ''))).strip().lower()

        if not name:
            return public.returnMsg(False, 'Invalid service name!')

        allowed_actions = ['start', 'stop', 'restart', 'reload', 'enable', 'disable', 'mask', 'unmask', 'reset-failed']
        if action not in allowed_actions:
            return public.returnMsg(False, 'Unsupported action: ' + action)

        code, out, err = self._run_cmd(['systemctl', action, name])
        if code == 0:
            msg_map = {
                'start': f'Service [{name}] started successfully!',
                'stop': f'Service [{name}] stopped successfully!',
                'restart': f'Service [{name}] restarted successfully!',
                'reload': f'Service [{name}] configuration reloaded successfully!',
                'enable': f'Service [{name}] enabled at system boot!',
                'disable': f'Service [{name}] disabled at system boot!',
                'mask': f'Service [{name}] masked!',
                'unmask': f'Service [{name}] unmasked!',
                'reset-failed': f'Reset failed state for [{name}] successfully!'
            }
            return public.returnMsg(True, msg_map.get(action, f'Action {action} completed successfully!'))
        else:
            detail = err if err else out
            return public.returnMsg(False, f'Failed to execute {action}: {detail}')

    def get_service_detail(self, get):
        """
        Retrieve service details: status, journal logs, properties, and .service unit file content
        """
        name = self._ensure_service_suffix(getattr(get, 'service_name', ''))
        if not name:
            return public.returnMsg(False, 'Invalid service name!')

        # systemctl show
        props = ['Id', 'Description', 'LoadState', 'ActiveState', 'SubState', 'UnitFileState', 'FragmentPath', 'MainPID', 'MemoryCurrent', 'ActiveEnterTimestamp', 'ExecStart']
        cmd_show = ['systemctl', 'show', name, f'--property={",".join(props)}']
        _, out_show, _ = self._run_cmd(cmd_show)

        show_data = {}
        for line in out_show.splitlines():
            if '=' in line:
                k, v = line.split('=', 1)
                show_data[k.strip()] = v.strip()

        # systemctl status
        _, out_status, err_status = self._run_cmd(['systemctl', 'status', name, '--no-pager', '-l', '-n', '25'])
        status_text = out_status if out_status else err_status

        # journalctl logs
        _, out_logs, _ = self._run_cmd(['journalctl', '-u', name, '-n', '50', '--no-pager'])

        fragment_path = show_data.get('FragmentPath', '')
        unit_content = ''
        is_custom = False

        if fragment_path and os.path.exists(fragment_path):
            try:
                with open(fragment_path, 'r', encoding='utf-8', errors='ignore') as f:
                    unit_content = f.read()
            except Exception as e:
                unit_content = f"# Unable to read file: {str(e)}"

        if fragment_path.startswith('/etc/systemd/system/') and not os.path.islink(fragment_path):
            is_custom = True
        elif os.path.exists(os.path.join(self.__systemd_custom_path, name)):
            is_custom = True

        data = {
            'name': name,
            'description': show_data.get('Description', ''),
            'load_state': show_data.get('LoadState', ''),
            'active_state': show_data.get('ActiveState', ''),
            'sub_state': show_data.get('SubState', ''),
            'unit_file_state': show_data.get('UnitFileState', ''),
            'main_pid': show_data.get('MainPID', '0'),
            'memory': self._format_memory(show_data.get('MemoryCurrent', 0)),
            'active_since': show_data.get('ActiveEnterTimestamp', '-'),
            'fragment_path': fragment_path,
            'is_custom': is_custom,
            'status_text': status_text,
            'recent_logs': out_logs,
            'unit_content': unit_content
        }

        return {'status': True, 'data': data}

    def get_service_logs(self, get):
        """
        Retrieve journal logs of service
        """
        name = self._ensure_service_suffix(getattr(get, 'service_name', ''))
        if not name:
            return public.returnMsg(False, 'Invalid service name!')

        try:
            lines = int(getattr(get, 'lines', 100))
            if lines < 10: lines = 10
            if lines > 1000: lines = 1000
        except:
            lines = 100

        _, out_logs, err_logs = self._run_cmd(['journalctl', '-u', name, '-n', str(lines), '--no-pager'])
        log_text = out_logs if out_logs else err_logs
        if not log_text:
            log_text = "(No logs recorded for this service yet)"

        return {'status': True, 'data': log_text}

    def add_service(self, get):
        """
        Add new custom service to /etc/systemd/system/
        """
        name = self._ensure_service_suffix(getattr(get, 'name', ''))
        if not name:
            return public.returnMsg(False, 'Invalid service name! Use letters, numbers, hyphens, and underscores only.')

        file_path = os.path.join(self.__systemd_custom_path, name)
        if os.path.exists(file_path):
            return public.returnMsg(False, f'Service [{name}] already exists at {file_path}!')

        raw_content = getattr(get, 'raw_content', '').strip()

        if raw_content:
            content = raw_content
        else:
            desc = getattr(get, 'description', '').strip() or name
            exec_start = getattr(get, 'exec_start', '').strip()
            working_dir = getattr(get, 'working_dir', '').strip()
            user = getattr(get, 'user', 'root').strip() or 'root'
            group = getattr(get, 'group', '').strip() or user
            restart = getattr(get, 'restart', 'always').strip() or 'always'
            restart_sec = getattr(get, 'restart_sec', '5s').strip() or '5s'
            service_type = getattr(get, 'service_type', 'simple').strip() or 'simple'
            env_vars = getattr(get, 'env', '').strip()

            if not exec_start:
                return public.returnMsg(False, 'Execution command (ExecStart) cannot be empty!')

            lines = [
                "[Unit]",
                f"Description={desc}",
                "After=network.target",
                "",
                "[Service]",
                f"Type={service_type}",
                f"User={user}",
                f"Group={group}"
            ]

            if working_dir:
                lines.append(f"WorkingDirectory={working_dir}")

            lines.append(f"ExecStart={exec_start}")
            lines.append(f"Restart={restart}")
            lines.append(f"RestartSec={restart_sec}")

            if env_vars:
                for ev in env_vars.splitlines():
                    ev = ev.strip()
                    if ev and '=' in ev:
                        lines.append(f"Environment=\"{ev}\"")

            lines.extend([
                "",
                "[Install]",
                "WantedBy=multi-user.target",
                ""
            ])
            content = "\n".join(lines)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            os.chmod(file_path, 0o644)
        except Exception as e:
            return public.returnMsg(False, 'Failed to write service file: ' + str(e))

        # Reload systemd
        self._run_cmd(['systemctl', 'daemon-reload'])

        auto_enable = getattr(get, 'auto_enable', '0')
        if auto_enable == '1' or auto_enable is True or auto_enable == 'true':
            self._run_cmd(['systemctl', 'enable', name])

        auto_start = getattr(get, 'auto_start', '0')
        if auto_start == '1' or auto_start is True or auto_start == 'true':
            code, out, err = self._run_cmd(['systemctl', 'start', name])
            if code != 0:
                return public.returnMsg(True, f'Service [{name}] created, but failed to start: {err or out}')

        return public.returnMsg(True, f'Service [{name}] created successfully!')

    def save_service_file(self, get):
        """
        Save and update .service unit file
        """
        name = self._ensure_service_suffix(getattr(get, 'name', ''))
        content = getattr(get, 'content', '')

        if not name:
            return public.returnMsg(False, 'Invalid service name!')
        if not content.strip():
            return public.returnMsg(False, 'Service unit file content cannot be empty!')

        target_path = os.path.join(self.__systemd_custom_path, name)

        # Create backup if old file exists
        if os.path.exists(target_path):
            try:
                shutil.copy2(target_path, target_path + '.bak')
            except:
                pass

        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            os.chmod(target_path, 0o644)
        except Exception as e:
            return public.returnMsg(False, 'Failed to write service file: ' + str(e))

        # Daemon reload
        self._run_cmd(['systemctl', 'daemon-reload'])

        restart = getattr(get, 'restart', '0')
        if restart == '1' or restart is True or restart == 'true':
            code, out, err = self._run_cmd(['systemctl', 'restart', name])
            if code != 0:
                return public.returnMsg(True, f'Configuration saved, but failed to restart service: {err or out}')
            return public.returnMsg(True, f'Configuration saved and service [{name}] restarted successfully!')

        return public.returnMsg(True, f'Configuration file for [{name}] saved successfully!')

    def delete_service(self, get):
        """
        Delete custom service from /etc/systemd/system/
        """
        name = self._ensure_service_suffix(getattr(get, 'name', ''))
        if not name:
            return public.returnMsg(False, 'Invalid service name!')

        target_path = os.path.join(self.__systemd_custom_path, name)
        if not os.path.exists(target_path):
            return public.returnMsg(False, f'Only custom services located in {self.__systemd_custom_path} can be deleted!')

        if os.path.islink(target_path):
            return public.returnMsg(False, 'This is a system symlink and cannot be deleted directly!')

        # 1. Stop service
        self._run_cmd(['systemctl', 'stop', name])
        # 2. Disable auto-start
        self._run_cmd(['systemctl', 'disable', name])
        # 3. Delete unit file
        try:
            os.remove(target_path)
            # Remove backup file if exists
            bak_path = target_path + '.bak'
            if os.path.exists(bak_path):
                os.remove(bak_path)
        except Exception as e:
            return public.returnMsg(False, 'Failed to delete service file: ' + str(e))

        # 4. Reload daemon and reset failed
        self._run_cmd(['systemctl', 'daemon-reload'])
        self._run_cmd(['systemctl', 'reset-failed', name])

        return public.returnMsg(True, f'Service [{name}] has been completely removed from system!')

    def daemon_reload(self, get=None):
        """
        systemctl daemon-reload
        """
        code, out, err = self._run_cmd(['systemctl', 'daemon-reload'])
        if code == 0:
            return public.returnMsg(True, 'systemctl daemon-reload executed successfully!')
        return public.returnMsg(False, 'daemon-reload error: ' + (err or out))
