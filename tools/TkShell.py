import serial
import sys

# TODO: check other Waves / SHP devices (only tested on a Samsung Wave 723 GT-S7230E (firmware: S723EPMKB1) and 3 Samsung Star devices)

sin = serial.Serial(sys.argv[1])

ack = bytes([0x7F, 0x01, 0x00, 0x42, 0x01, 0x7E])

def crc16_cms(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            crc = (crc << 1) ^ 0x8005 if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return crc

# -------------------
# commands
# -------------------
RB_FM = 0x00
RB_NV = 0x01
RB_REG = 0x02
RB_MEM = 0x03
RB_ADM = 0x04
RB_MISC = 0x05
RB_SYS = 0x06
# -------------------
# subcommands (FM)
# -------------------
RB_ID_FM_OPENFILE = 0x00
RB_ID_FM_CLOSEFILE = 0x01
RB_ID_FM_READFILE = 0x02
RB_ID_FM_WRITEFILE = 0x03
RB_ID_FM_CREATEFILE = 0x04
RB_ID_FM_REMOVEFILE = 0x05
RB_ID_FM_MOVEFILE = 0x06
RB_ID_FM_GETFILEATTRIBUTES = 0x07
RB_ID_FM_OPENDIR = 0x08
RB_ID_FM_CLOSEDIR = 0x09
RB_ID_FM_READDIR = 0x0A
RB_ID_FM_CREATEDIR = 0x0B
RB_ID_FM_REMOVEDIR = 0x0C
# -------------------
# subcommands (NV)
# -------------------
RB_ID_NV_GETINT = 0x00
RB_ID_NV_GETSTRING = 0x01
RB_ID_NV_SETINT = 0x02
RB_ID_NV_SETSTRING = 0x03
RB_ID_NV_WRITEINT = 0x04
RB_ID_NV_WRITESTRING = 0x05
RB_ID_NV_FLUSH = 0x06
# -------------------
# subcommands (Reg)
# -------------------
RB_ID_REG_LOAD = 0x00
RB_ID_REG_UNLOAD = 0x01
RB_ID_REG_GETINT = 0x02
RB_ID_REG_unk_7d76fcfa = 0x03
RB_ID_REG_GETSTRING = 0x04
RB_ID_REG_SETINT = 0x05
RB_ID_REG_unk_7d770cd8 = 0x06
RB_ID_REG_SETSTRING = 0x07
# -------------------
# subcommands (Mem)
# -------------------
# nothing found, 0x00 default
# -------------------
# subcommands (Adm)
# -------------------
RB_ID_ADM_HELLO = 0x00
RB_ID_ADM_ECHO = 0x01
# -------------------
# subcommands (Misc)
# -------------------
# nothing found, 0x00 default
# -------------------
# subcommands (Sys)
# -------------------
RB_ID_SYS_GetGenLock = 0x00
RB_ID_SYS_SetGenLock = 0x01
RB_ID_SYS_GetNetLock = 0x02
RB_ID_SYS_SetNetLock = 0x03
RB_ID_SYS_GetSubLock = 0x04
RB_ID_SYS_SetSubLock = 0x05
RB_ID_SYS_GetSpLock = 0x06
RB_ID_SYS_SetSpLock = 0x07
RB_ID_SYS_GetCpLock = 0x08
RB_ID_SYS_SetCpLock = 0x09
RB_ID_SYS_GetMultiLock = 0x0A
RB_ID_SYS_SetMultiLock = 0x0B
RB_ID_SYS_GetSimLock = 0x0C
RB_ID_SYS_SetSimLock = 0x0D

# reading directories:
# PC to PHONE -> RB_FM with RB_ID_FM_OPENDIR, data: path as string
# PHONE to PC -> hDir
# PC to PHONE -> RB_FM with RB_ID_FM_READDIR, data: hDir as 32-bit LE int
# PHONE to PC -> directory list (byte structure still todo)

# getting NV strings:
# PC to PHONE -> RB_NV with RB_ID_NV_GETSTRING, data: uint LE: NV index
# PHONE to PC -> NV contents

# writing NV strings:
# PC to PHONE -> RB_NV with RB_ID_NV_SETSTRING, data: [uint LE: NV index] + [NULL terminated ASCII data, max 1 NVRAM block (512 bytes)]
# PHONE to PC -> NV contents

def buildcmd(data, command, subcommand):
    cmd = data
    crc = crc16_cms(bytes([subcommand]) + bytes([command]) + len(cmd).to_bytes(2, 'little') + cmd)
    packet = bytearray()
    packet.append(0x7F)
    packet.extend((len(cmd)+6).to_bytes(2, 'little'))
    packet.append(0x42)
    packet.append(subcommand) # originally a 16-bit ushort (0xAABB (AA - command, BB - subcommand))
    packet.append(command)
    packet.extend(len(cmd).to_bytes(2, 'little'))
    packet.extend(cmd)
    packet.extend(crc.to_bytes(2, 'big'))
    packet.append(0x7E)
    return packet

scmd = 0
cmd = RB_MISC
data = (sys.argv[2] + '\0').encode()

command = buildcmd(data, cmd, scmd) # TkShell is really the only interesting cmd to me lmao

sin.write(command)
print(f"sent to device: {command.hex()}")
i = 0
while (i < len(ack)):
    b = int.from_bytes(sin.read(1))
    if b != ack[i]:
        i = 0
    else:
        i += 1

print("\nresponse from device:")
print("="*25)

st = int.from_bytes(sin.read(1))
if (st != 0x7f):
    print(f"invalid OemUsbWrite packet (invalid start byte) (got: 0x{st:02X}, expected 0x7F)")
    exit()
size = int.from_bytes(sin.read(2), 'little')
B_thing = int.from_bytes(sin.read(1))
if (B_thing != 0x42):
    print(f"invalid OemUsbWrite packet (invalid byte) (got: 0x{B_thing:02X}, expected 0x42)")
    exit()
respSubcommand = int.from_bytes(sin.read(1))
respCommand = int.from_bytes(sin.read(1))
if (respCommand != cmd):
    print("invalid OemUsbWrite packet (response command does not match sender)")
    exit()
if (respSubcommand != scmd):
    print("invalid OemUsbWrite packet (response subcommand does not match sender)")
    exit()
print(f"command: {respCommand:02X}")
print(f"subcommand: {respSubcommand:02X}")
respDataLen = int.from_bytes(sin.read(2), 'little')
respData = sin.read(respDataLen)
crc = int.from_bytes(sin.read(2))
endbyte = int.from_bytes(sin.read(1))
if (endbyte != 0x7e):
    print(f"invalid OemUsbWrite packet (invalid end byte) (got: 0x{endbyte:02X}, expected 0x7E)")
    exit()
print(f"returned data: {respData.hex()}")
crcCalc = crc16_cms(bytes([respSubcommand]) + bytes([respCommand]) + len(respData).to_bytes(2, 'little') + respData)
crcMatch = False
if crc == crcCalc:
    crcMatch = True
print(f"CRC: {crc:04X} (verified: {crcMatch})")
