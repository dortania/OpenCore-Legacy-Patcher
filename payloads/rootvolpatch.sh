#!/bin/bash
set -eux

if [[ ! -f "/System/Library/.dortania-patched" ]]; then
GUIUSER='0 root'

while [[ ${GUIUSER} == '0 root' ]]
do
GUIUSER=$(stat -f '%u %Su' /dev/console)
done

sleep 10
osascript -e 'display alert "Beginning to apply post-install patches" message "Your Mac may become unresponsive during this process. Please wait for the next notification confirming that root volume patching successfully completed and do not turn off your computer."' 
sleep 2

cd /Library/Dortania
/Library/Dortania/OpenCore-Patcher --patch_sys_vol --cli_offline || ( osascript -e 'display alert "Failed to apply patches" message "Try restarting your Mac."' && exit 1 )

osascript -e 'display alert "Finished applying patches" message "When you press OK, your Mac will reboot."'
shutdown -r now

fi
