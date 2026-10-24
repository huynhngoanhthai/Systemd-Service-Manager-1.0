#!/bin/bash
PATH=/www/server/panel/pyenv/bin:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
install_tmp='/tmp/bt_install.pl'

plugin_name="service_manager"
plugin_path="/www/server/panel/plugin/${plugin_name}"

Install_plugin()
{
	mkdir -p "${plugin_path}"
	echo 'The installation is complete' > $install_tmp
}

Uninstall_plugin()
{
	rm -rf "${plugin_path}"
}

action=$1
if [ "${1}" == 'install' ];then
	Install_plugin
else
	Uninstall_plugin
fi
