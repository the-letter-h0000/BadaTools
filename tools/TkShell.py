import serial
import sys
import time

# TODO: check other Waves / SHP devices (only tested on a Samsung Wave 723 GT-S7230E (firmware: S723EPMKB1))

sin = serial.Serial(sys.argv[1])

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
# TODO: check others
RB_FM = 0x00
RB_NV = 0x01
RB_REG = 0x02
RB_MEM = 0x03
RB_ADM = 0x04 # noop command?? ([869559 3970 849.178 P00.T-1.D001.G-1.E-01:0000 ALL       > )[869559 __RbHandleAdm: Got Hello command.)
RB_MISC = 0x05
RB_SYS = 0x06
# -------------------
# subcommands (FM)
# -------------------
# TODO: check them
RB_ID_FM_CLOSEFILE = 0x00 # unknown
RB_ID_FM_OPENFILE = 0x01
RB_ID_FM_READFILE = 0x02
RB_ID_FM_WRITEFILE = 0x03
RB_ID_FM_CREATEFILE = 0x04
RB_ID_FM_REMOVEFILE = 0x05
RB_ID_FM_MOVEFILE = 0x06
RB_ID_FM_OPENDIR = 0x08
RB_ID_FM_CREATEDIR = 0x09
RB_ID_FM_READDIR = 0x0A
RB_ID_FM_CLOSEDIR = 0x0B
RB_ID_FM_REMOVEDIR = 0x0C
RB_ID_FM_GETFILEATTRIBUTES = 0x0D

def buildcmd(data, subcommand, command):
    cmd = data.encode() + b"\0"
    crc = crc16_cms(bytes([subcommand]) + bytes([command]) + len(cmd).to_bytes(2, 'little') + cmd)
    packet = bytearray()
    packet.append(0x7F)
    packet.extend((len(cmd)+6).to_bytes(2, 'little'))
    packet.append(0x42)
    packet.append(subcommand)
    packet.append(command)
    packet.extend(len(cmd).to_bytes(2, 'little'))
    packet.extend(cmd)
    packet.extend(crc.to_bytes(2, 'big'))
    packet.append(0x7E)
    return packet

command = buildcmd(sys.argv[2], 0, RB_MISC) # TkShell is really the only interesting cmd to me lmao

sin.write(command)
print(f"sent to device: {command.hex()}")
time.sleep(0.5)
if (sin.read(1) == b"\x7F"):
    # skip mystery packet
    sin.read(5)

if sin.read(1) != b"\x7F":
    print("invalid response")
    exit(1)

sin.read(5)
payloadlen = int.from_bytes(sin.read(2), 'little')
payload = sin.read(payloadlen)
print(f"return value: {int.from_bytes(payload, 'little')}")