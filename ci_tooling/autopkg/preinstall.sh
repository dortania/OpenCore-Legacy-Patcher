#!/bin/sh
app_path="/Library/Application Support/Dortania/OpenCore-Patcher.app"
launch_agent_path="/Library/LaunchAgents/com.dortania.opencore-legacy-patcher.auto-patch.plist"
if [ -d "$app_path" ]; then
    echo "Found OpenCore-Patcher.app, removing..."
    rm -rf "$app_path"
fi

if [ -f "$launch_agent_path" ]; then
    echo "Found launch agent, removing..."
    rm -f "$launch_agent_path"
fi
