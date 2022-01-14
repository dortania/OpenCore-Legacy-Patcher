
path = './dist/OpenCore-Patcher.app/Contents/MacOS/OpenCore-Patcher'
find = b'\x00\x0D\x0A\x00'
replace = b'\x00\x0A\x0A\x00'
# Open file in binary mode
with open(path, 'rb') as f:
    data = f.read()
    data = data.replace(find, replace)
    with open(path, 'wb') as f:
        f.write(data)