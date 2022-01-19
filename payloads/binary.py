# Patches LC_VERSION_MIN_MACOSX in Load Command to report 10.10
#
# By default Pyinstaller will create binaries supporting 10.13+
# However this limitation is entirely arbitrary for our libraries
# and instead we're able to support 10.10 without issues.
# 
# To verify set version:
#   otool -l ./dist/OpenCore-Patcher.app/Contents/MacOS/OpenCore-Patcher
# 
#       cmd LC_VERSION_MIN_MACOSX
#   cmdsize 16
#   version 10.13
#       sdk 10.9

path = './dist/OpenCore-Patcher.app/Contents/MacOS/OpenCore-Patcher'
find = b'\x00\x0D\x0A\x00' # 10.13 (0xA0D)
replace = b'\x00\x0A\x0A\x00' # 10.10 (0xA0A)
with open(path, 'rb') as f:
    data = f.read()
    data = data.replace(find, replace)
    with open(path, 'wb') as f:
        f.write(data)