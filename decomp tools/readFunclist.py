file = open("uncompress_apps.bin", "rb")
print("opened uncompress_apps.bin")
file.seek(0x04340000)
size = int.from_bytes(file.read(4), 'little') - 8
CAFECAFE = int.from_bytes(file.read(4), 'little')
if CAFECAFE != 0xCAFECAFE:
    print(f"ERROR: uncompress_apps.bin is NOT valid (0x04340004 is NOT 0xCAFECAFE, got 0x{CAFECAFE:08X})")
    exit()
print(f"size: 0x{size:08X}")
if (size % 44 != 0):
    print(f"ERROR: uncompress_apps is NOT mod 44 = 0 (mod result: {size % 44})")
    exit()
print(f"functions: {size // 44}")
for i in range(size // 44):
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
