file = open("funclist.bin", "rb") # uncompress_apps.bin, 0x04340008, 0x04E29953
print("opened funclist.bin")
a = file.read()
file.seek(0)
if (len(a) % 44 != 0):
    print("ERROR: funclist is NOT mod 44 = 0")
    exit()
for i in range(len(a) // 44):
    # read the name of the function
    funcname = file.read(36)
    # read the LE start address
    startaddr = file.read(4)
    # read the LE end address
    endaddr = file.read(4)
    # shift addresses to match Ghidra
    startaddr_fixed = int.from_bytes(startaddr, 'little') & ~1 # remove the Thumb bit (the Wave 723 uses ARM:LE:32:v8)
    endaddr_fixed = int.from_bytes(endaddr, 'little') & ~1 # see above comment
    if startaddr_fixed < 0x81000000: # magic that i found out because of my idea to try GOTOing to (startaddr) - 0x81000000 in HxD in the firmware and it actually worked and yeeted me to the exact function
        print(f"start: 0x{startaddr_fixed:08X} (0x{(startaddr_fixed + 0x5D80000):08X}), end: 0x{endaddr_fixed:08X} (0x{(endaddr_fixed + 0x5D80000):08X}) - {funcname.strip(b'\0').decode()}") # see SamsunWaveDecompilation ADDRESSES.txt for more info... or not
    else:
        print(f"start: 0x{startaddr_fixed:08X}, end: 0x{endaddr_fixed:08X} - {funcname.strip(b'\0').decode()}")
file.close()
