#!/bin/sh

# Modified by Jazzzny for OpenCore Legacy Patcher on 06.10.23.

abort() {
  echo "Fatal error: ${1}!"
  exit 1
}

# shellcheck disable=SC2317
cleanup() {
  rm -rf "${KeyPath}"
}

if [ ! -x /usr/bin/dirname ] || [ ! -x /bin/chmod ] || [ ! -x /bin/mkdir ] || [ ! -x /bin/rm ] || [ ! -x /usr/bin/grep ] || [ ! -x /usr/bin/awk ] || [ ! -x /bin/dd ] || [ ! -x /usr/bin/uuidgen ] ; then
  abort "Unix environment is broken!"
fi

cd "$(/usr/bin/dirname "$0")" || abort "Failed to enter working directory!"

OCPath="$1"

if [ "$OCPath" = "" ]; then
  OCPath=../../EFI/OC
fi

KeyPath="/tmp/$(/usr/bin/uuidgen)"
OCBin="${OCPath}/OpenCore.efi"
PubKey="${KeyPath}/vault.pub"

if [ ! -d "${OCPath}" ]; then
  abort "Path ${OCPath} is missing!"
fi

if [ ! -f "${OCBin}" ]; then
  abort "OpenCore.efi is missing!"
fi

if [ ! -x ./RsaTool ] || [ ! -x ./create_vault.sh ]; then
  if [ -f ./RsaTool ]; then
    /bin/chmod a+x ./RsaTool || abort "Failed to set permission for RsaTool"
  else
    abort "Failed to find RsaTool!"
  fi

  if [ -f ./create_vault.sh ]; then
    /bin/chmod a+x ./create_vault.sh || abort "Failed to set permission for create_vault.sh"
  else
    abort "Failed to find create_vault.sh!"
  fi
fi

trap cleanup EXIT INT TERM

if [ ! -d "${KeyPath}" ]; then
  /bin/mkdir -p "${KeyPath}" || abort "Failed to create path ${KeyPath}"
fi

./create_vault.sh "${OCPath}" || abort "create_vault.sh returns errors!"

echo "Signing OpenCore..."
./RsaTool -sign "${OCPath}/vault.plist" "${OCPath}/vault.sig" "${PubKey}" || abort "Failed to patch ${PubKey}"
off=$(($(./strings -a -t d "${OCBin}" | /usr/bin/grep "=BEGIN OC VAULT=" | /usr/bin/awk '{print $1}') + 16))
if [ "${off}" -le 16 ]; then
  abort "${OCBin} is borked"
fi

/bin/dd of="${OCBin}" if="${PubKey}" bs=1 seek="${off}" count=528 conv=notrunc || abort "Failed to bin-patch ${OCBin}"

echo "Signing complete"
exit 0
