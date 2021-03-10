#!/bin/sh

abort() {
  echo "Fatal error: ${1}!"
  exit 1
}

cleanup() {
  echo "Cleaning up keys"
  rm -rf "${KeyPath}"
}

if [ ! -x /usr/bin/dirname ] || [ ! -x /bin/chmod ] || [ ! -x /bin/mkdir ] || [ ! -x /usr/bin/openssl ] || [ ! -x /bin/rm ] || [ ! -x /usr/bin/strings ] || [ ! -x /usr/bin/grep ] || [ ! -x /usr/bin/cut ] || [ ! -x /bin/dd ] || [ ! -x /usr/bin/uuidgen ] ; then
  abort "Unix environment is broken!"
fi

cd "$(/usr/bin/dirname "$0")" || abort "Failed to enter working directory!"

OCPath="$1"

if [ "$OCPath" = "" ]; then
  OCPath=../../EFI/OC
fi

KeyPath="/tmp/Keys-$(/usr/bin/uuidgen)"
OCBin="${OCPath}/OpenCore.efi"
RootCA="${KeyPath}/ca.pem"
PrivKey="${KeyPath}/privatekey.cer"
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

if [ ! -f "${RootCA}" ]; then
  /usr/bin/openssl genrsa -out "${RootCA}" 2048 || abort "Failed to generate CA"
  if [ -f "${PrivKey}" ]; then
    echo "WARNING: Private key exists without CA"
  fi
fi

/bin/rm -fP "${PrivKey}" || abort "Failed to remove ${PrivKey}"
echo "Issuing a new private key..."
/usr/bin/openssl req -new -x509 -key "${RootCA}" -out "${PrivKey}" -days 1825 -subj "/C=WO/L=127.0.0.1/O=Acidanthera/OU=Acidanthera OpenCore/CN=Greetings from Acidanthera and WWHC" || abort "Failed to issue private key!"

/bin/rm -fP "${PubKey}" || abort "Failed to remove ${PubKey}"
echo "Getting public key based off private key..."
./RsaTool -cert "${PrivKey}" > "${PubKey}" || abort "Failed to get public key"

echo "Signing ${OCBin}..."
./RsaTool -sign "${OCPath}/vault.plist" "${OCPath}/vault.sig" "${PubKey}" || abort "Failed to patch ${PubKey}"

echo "Bin-patching ${OCBin}..."
off=$(($(/usr/bin/strings -a -t d "${OCBin}" | /usr/bin/grep "=BEGIN OC VAULT=" | /usr/bin/cut -f1 -d' ') + 16))
if [ "${off}" -le 16 ]; then
  abort "${OCBin} is borked"
fi

/bin/dd of="${OCBin}" if="${PubKey}" bs=1 seek="${off}" count=528 conv=notrunc || abort "Failed to bin-patch ${OCBin}"

echo "All done!"
exit 0
