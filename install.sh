#!/bin/bash
PATH=/www/server/panel/pyenv/bin:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
install_tmp='/tmp/bt_install.pl'

plugin_name="service_manager"
plugin_path="/www/server/panel/plugin/${plugin_name}"
repo_url="https://github.com/huynhngoanhthai/Systemd-Service-Manager-1.0.git"
zip_url="https://github.com/huynhngoanhthai/Systemd-Service-Manager-1.0/archive/refs/heads/main.zip"
script_dir="$(cd "$(dirname "$0")" && pwd)"

Fetch_and_update_files()
{
	echo "Updating ${plugin_name} to the latest version..."
	mkdir -p "${plugin_path}"

	# Case 1: Running from an external directory with plugin files present
	if [ "${script_dir}" != "${plugin_path}" ] && [ -f "${script_dir}/info.json" ] && [ -f "${script_dir}/service_manager_main.py" ]; then
		echo "Copying update files from ${script_dir} to ${plugin_path}..."
		cp -rf "${script_dir}"/* "${plugin_path}/"
		return 0
	fi

	# Case 2: Git repository in plugin directory
	if [ -d "${plugin_path}/.git" ] && command -v git >/dev/null 2>&1; then
		echo "Git repository found in ${plugin_path}. Pulling latest changes..."
		git config --global --add safe.directory "${plugin_path}" 2>/dev/null || true
		(
			cd "${plugin_path}" || exit 1
			git fetch --all 2>/dev/null
			if git reset --hard origin/main 2>/dev/null || git reset --hard origin/master 2>/dev/null || git pull origin main 2>/dev/null; then
				echo "Git update successful."
				exit 0
			fi
			exit 1
		)
		if [ $? -eq 0 ]; then
			return 0
		fi
		echo "Git pull failed or branch mismatch. Falling back to archive download..."
	fi

	# Case 3: Download main.zip from GitHub
	tmp_dir="/tmp/sm_update_$$"
	rm -rf "$tmp_dir"
	mkdir -p "$tmp_dir"

	downloaded=0
	if command -v curl >/dev/null 2>&1; then
		echo "Downloading latest version using curl..."
		curl -sSL -o "${tmp_dir}/main.zip" "${zip_url}" && downloaded=1
	elif command -v wget >/dev/null 2>&1; then
		echo "Downloading latest version using wget..."
		wget -q -O "${tmp_dir}/main.zip" "${zip_url}" && downloaded=1
	fi

	if [ "$downloaded" -eq 1 ] && [ -s "${tmp_dir}/main.zip" ]; then
		if command -v unzip >/dev/null 2>&1; then
			echo "Extracting latest version files..."
			unzip -qo "${tmp_dir}/main.zip" -d "${tmp_dir}"
			extracted_folder=$(find "${tmp_dir}" -maxdepth 1 -type d -name "Systemd-Service-Manager*" | head -n 1)
			if [ -n "${extracted_folder}" ] && [ -d "${extracted_folder}" ]; then
				cp -rf "${extracted_folder}"/* "${plugin_path}/"
				rm -rf "${tmp_dir}"
				echo "ZIP update successful."
				return 0
			fi
		else
			echo "Warning: unzip utility is not installed."
		fi
	fi
	rm -rf "${tmp_dir}"

	# Case 4: Shallow git clone fallback
	if command -v git >/dev/null 2>&1; then
		echo "Attempting shallow git clone to temporary directory..."
		tmp_clone="/tmp/sm_git_clone_$$"
		rm -rf "${tmp_clone}"
		if git clone --depth 1 "${repo_url}" "${tmp_clone}" 2>/dev/null; then
			cp -rf "${tmp_clone}"/* "${plugin_path}/"
			rm -rf "${tmp_clone}"
			echo "Git clone update successful."
			return 0
		fi
		rm -rf "${tmp_clone}"
	fi

	echo "Notice: Could not download remote update; keeping existing files."
	return 0
}

Install_plugin()
{
	# If plugin is already installed, update to the latest version
	if [ -d "${plugin_path}" ] && [ -f "${plugin_path}/service_manager_main.py" ]; then
		echo "Plugin ${plugin_name} already exists. Updating to latest version..."
		Update_plugin
		return 0
	fi

	echo "Installing ${plugin_name}..."
	mkdir -p "${plugin_path}"

	if [ "${script_dir}" != "${plugin_path}" ] && [ -f "${script_dir}/info.json" ]; then
		cp -rf "${script_dir}"/* "${plugin_path}/"
	else
		Fetch_and_update_files
	fi

	chmod +x "${plugin_path}"/*.sh 2>/dev/null || true
	chmod -R 755 "${plugin_path}" 2>/dev/null || true

	echo 'The installation is complete' > $install_tmp
	echo 'Successify'
}

Update_plugin()
{
	echo "Updating ${plugin_name}..."
	Fetch_and_update_files

	chmod +x "${plugin_path}"/*.sh 2>/dev/null || true
	chmod -R 755 "${plugin_path}" 2>/dev/null || true

	echo 'The update is complete' > $install_tmp
	echo 'The installation is complete' > $install_tmp
	echo 'Successify'
}

Uninstall_plugin()
{
	echo "Uninstalling ${plugin_name}..."
	rm -rf "${plugin_path}"
	echo 'The uninstall is complete' > $install_tmp
	echo 'Successify'
}

action=$1
if [ "${action}" == 'install' ]; then
	Install_plugin
elif [ "${action}" == 'update' ] || [ "${action}" == 'upgrade' ]; then
	Update_plugin
elif [ "${action}" == 'uninstall' ]; then
	Uninstall_plugin
else
	# If no argument or unknown argument, do not uninstall
	if [ -d "${plugin_path}" ] && [ -f "${plugin_path}/service_manager_main.py" ]; then
		Update_plugin
	else
		Install_plugin
	fi
fi
