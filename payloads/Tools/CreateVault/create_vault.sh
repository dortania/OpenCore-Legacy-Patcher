#!/bin/bash

#  create_vault.sh
#
#
#  Created by Rodion Shingarev on 13.04.19.
#  Modified by Jazzzny for OpenCore Legacy Patcher on 06.10.23.
#
OCPath="$1"
UtilsPath="$PWD"

if [ "${OCPath}" = "" ]; then
  echo "Usage ./create_vault.sh path/to/EFI/OC"
  exit 1
fi

if [ ! -d "${OCPath}" ]; then
  echo "Path $OCPath is missing!"
  exit 1
fi

if [ ! -x /usr/bin/env ] || [ ! -x /usr/bin/find ] || [ ! -x /bin/rm ] || [ ! -x /usr/bin/sed ] || [ ! -x /usr/bin/awk ] || [ ! -x /usr/bin/sort ] || [ ! -x /usr/bin/xxd ]; then
  echo "Unix environment is broken!"
  exit 1
fi

abort() {
  /bin/rm -rf vault.plist vault.sig /tmp/vault_hash
  echo "Fatal error: ${1}!"
  exit 1
}

# plist output functions so we don't need PlistBuddy
write_header() {
  cat <<EOF > "$1"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Files</key>
	<dict>
EOF
}

write_file_name_and_hash() {
  {
    echo -e "\t\t<key>${2}</key>"
    echo -e "\t\t<data>"
    echo -e -n "\t\t"
    cat "$3"
    echo -e "\t\t</data>"
  } >> "$1"
}

write_footer() {
  cat <<EOF >> "$1"
	</dict>
	<key>Version</key>
	<integer>1</integer>
</dict>
</plist>
EOF
}

cd "${OCPath}" || abort "Failed to reach ${OCPath}"
/bin/rm -rf vault.plist vault.sig || abort "Failed to cleanup"

echo "Hashing OpenCore configuration..."

write_header vault.plist

/usr/bin/find . -not -path '*/\.*' -type f \
  \( ! -iname ".*" \) \
  \( ! -iname "vault.*" \) \
  \( ! -iname "MemTest86.log" \) \
  \( ! -iname "MemTest86-Report-*.html" \) \
  \( ! -iname "OpenCore.efi" \) | env LC_COLLATE=POSIX /usr/bin/sort | while read -r fname; do
  fname="${fname#"./"}"
  wname="${fname//\//\\\\}"
  sha=$("${UtilsPath}"/openssl sha256 "${fname}" | /usr/bin/awk '{print $2}') || abort "Failed to hash ${fname}"
  if [ "${#sha}" != 64 ] || [ "$(echo "$sha"| /usr/bin/sed 's/^[a-f0-9]*$//')" ]; then
    abort "Got invalid hash: ${sha}!"
  fi

  echo "${sha}" | /usr/bin/xxd -r -p | "${UtilsPath}"/openssl base64 > /tmp/vault_hash || abort "Hashing failure"
  write_file_name_and_hash vault.plist "${wname}" /tmp/vault_hash
done

/bin/rm -rf /tmp/vault_hash

write_footer vault.plist

exit 0
