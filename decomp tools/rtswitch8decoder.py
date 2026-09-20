# ARMv6 __rt_switch8 decoder

hexstr = input("bytes after BLX __rt_switch8 > ")
switchdata = bytes.fromhex(hexstr)
print(f"max cases: {switchdata[0]} + 1 default")
sbaseaddr = input("absolute address of 1st byte after BLX __rt_switch8 > ")
baseaddr = int.from_bytes(bytes.fromhex(sbaseaddr), "big")
i = 0
for j in range(1, switchdata[0] + 2):
    if j == switchdata[0] + 1:
        print(f"default -> {(baseaddr + (switchdata[j] * 2)):08X}") # * 2 because Thumb is aligned for 2 byte instructions
    else:
        print(f"case {i} -> {(baseaddr + (switchdata[j] * 2)):08X}")
    i += 1