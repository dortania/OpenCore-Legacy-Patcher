#!/bin/bash

#  create_vault.sh
#
#
#  Created by Rodion Shingarev on 13.04.19.
#
OCPath="$1"

if [ "${OCPath}" = "" ]; then
  echo "Usage ./create_vault.sh path/to/EFI/OC"
  exit 1
fi

if [ ! -d "${OCPath}" ]; then
  echo "Path $OCPath is missing!"
  exit 1
fi

if [ ! -x /usr/bin/find ] || [ ! -x /bin/rm ] || [ ! -x /usr/bin/sed ] || [ ! -x /usr/bin/xxd ]; then
  echo "Unix environment is broken!"
  exit 1
fi

if [ ! -x /usr/libexec/PlistBuddy ]; then
  echo "PlistBuddy is missing!"
  exit 1
fi

if [ ! -x /usr/bin/shasum ]; then
  echo "shasum is missing!"
  exit 1
fi

abort() {
  /bin/rm -rf vault.plist vault.sig /tmp/vault_hash
  echo "Fatal error: ${1}!"
  exit 1
}

echo "Chose ${OCPath} for hashing..."

cd "${OCPath}" || abort "Failed to reach ${OCPath}"
/bin/rm -rf vault.plist vault.sig || abort "Failed to cleanup"
/usr/libexec/PlistBuddy -c "Add Version integer 1" vault.plist || abort "Failed to set vault.plist version"

echo "Hashing files in ${OCPath}..."

/usr/bin/find . -not -path '*/\.*' -type f \
  \( ! -iname ".*" \) \
  \( ! -iname "vault.*" \) \
  \( ! -iname "OpenCore.efi" \) | while read -r fname; do
  fname="${fname#"./"}"
  wname="${fname//\//\\\\}"
  shasum=$(/usr/bin/shasum -a 256 "${fname}") || abort "Failed to hash ${fname}"
  sha=$(echo "$shasum" | /usr/bin/sed 's/^\([a-f0-9]\{64\}\).*/\1/') || abort "Illegit hashsum"
  if [ "${#sha}" != 64 ] || [ "$(echo "$sha"| /usr/bin/sed 's/^[a-f0-9]*$//')" ]; then
    abort "Got invalid hash: ${sha}!"
  fi

  echo "${wname}: ${sha}"

  echo "${sha}" | /usr/bin/xxd -r -p > /tmp/vault_hash || abort "Hashing failure"
  /usr/libexec/PlistBuddy -c "Import Files:'${wname}' /tmp/vault_hash" vault.plist || abort "Failed to append vault.plist!"
done

/bin/rm -rf /tmp/vault_hash

echo "All done!"
exit 0
