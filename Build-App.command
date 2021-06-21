#!/usr/bin/env bash
printf "OpenCore-Patcher.app Builder"
printf "\nNot supported by end users, please use prebuilt binaries"
printf "\neither on Github Release or Nightly Builds from Github Actions:"
printf "\n\nOffical Release: \n- https://github.com/dortania/OpenCore-Legacy-Patcher/releases"
printf "\n\nNightly Builds: \n- https://nightly.link/dortania/OpenCore-Legacy-Patcher/workflows/build-app/main/OpenCore-Patcher.app.zip\n\n"
read -n 1 -s -r -p "Press any key to continue: "
if which python3 > /dev/null 2>&1;
then
    printf "\nPython found, continuing"
    printf "\nUpdating Requests and pyinstaller\n"
    pip3 install --upgrade pyinstaller requests
    printf "\nBuilding app"
    pyinstaller OpenCore-Patcher.spec
    ./after_pyinstaller.sh
    open ./dist/
else
    printf "\nPython is missing! Cannot build OpenCore-Patcher.app\n"
fi