#!/usr/bin/env bash
folder=Audio.$(date "+%Y.%m.%d-%H.%M")
mkdir -p ~/Desktop/$folder
ioreg -l -w0 > ~/Desktop/$folder/Audio-IOReg.txt
log show --last boot > ~/Desktop/$folder/Audio-log-boot.txt
sudo dmesg > ~/Desktop/$folder/Audio-DMESG.txt