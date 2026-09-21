import serial
import time
import serial.tools.list_ports

# SamsungSHPForgottenPasswordGetter.py - new version of forgotten password getter, directly uses NVRAM reads instead of dumping RAM in Upload Mode

comport = serial.Serial()

RB_NV = 0x01
RB_ID_NV_GETINT = 0x00
RB_ID_NV_GETSTRING = 0x01
RB_ID_NV_SETINT = 0x02
RB_ID_NV_SETSTRING = 0x03
RB_ID_NV_WRITEINT = 0x04
RB_ID_NV_WRITESTRING = 0x05
RB_ID_NV_FLUSH = 0x06

ack = bytes([0x7F, 0x01, 0x00, 0x42, 0x01, 0x7E])

logs = False

def lprint(txt):
    if logs:
        print(txt)

def crc16_cms(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            crc = (crc << 1) ^ 0x8005 if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return crc

def sendAT(command, sp=comport):
    lprint(f"send AT: {command}")
    sp.write(command.encode('utf-8') + b"\r\n")
    time.sleep(50 / 1000)
    b = bytearray()
    while sp.in_waiting > 0:
        b.extend(sp.read_all())
        time.sleep(20 / 1000)
    rawresponse = b.decode('utf-8', errors='replace').strip()
    lines = rawresponse.splitlines()
    lastline = len(lines)-1
    if len(lines) == 0 or not lines[lastline].startswith("OK"):
        return None
    else:
        if command in lines[0]:
            return "\n".join(lines[1:lastline]).strip()
        else:
            return "\n".join(lines[0:lastline]).strip()

def buildcmd(data, subcommand, command):
    crc = crc16_cms(bytes([subcommand]) + bytes([command]) + len(data).to_bytes(2, 'little') + data)
    packet = bytearray()
    packet.append(0x7F)
    packet.extend((len(data)+6).to_bytes(2, 'little'))
    packet.append(0x42)
    packet.append(subcommand)
    packet.append(command)
    packet.extend(len(data).to_bytes(2, 'little'))
    packet.extend(data)
    packet.extend(crc.to_bytes(2, 'big'))
    packet.append(0x7E)
    return packet

def getWaveDevice():
    x = serial.Serial()
    for port in serial.tools.list_ports.comports():
        if port.product == "Wave723" or port.product == "Mobile USB Modem 1.0":
            x.port = port.device
            x.open()
            if sendAT("AT", x) == "":
                x.close()
                print(f"found device on {port.device}")
                return port.device
            else:
                x.close()
    return None

def waitForWave():
    print("waiting for device...")
    x = None
    while True:
        x = getWaveDevice()
        if x != None:
            return x
        time.sleep(2)

def parseTkShell():
    i = 0
    while (i < len(ack)):
        b = int.from_bytes(comport.read(1))
        if b != ack[i]:
            i = 0
        else:
            i += 1

    lprint("\nresponse from device:")
    lprint("="*25)

    st = int.from_bytes(comport.read(1))
    if (st != 0x7f):
        print(f"invalid OemUsbWrite packet (invalid start byte) (got: 0x{st:02X}, expected 0x7F)")
        return None
    comport.read(2) # ignore packet size
    B_thing = int.from_bytes(comport.read(1))
    if (B_thing != 0x42):
        print(f"invalid OemUsbWrite packet (invalid byte) (got: 0x{B_thing:02X}, expected 0x42)")
        return None
    comport.read(2) # ignore subcommand and command
    respDataLen = int.from_bytes(comport.read(2), 'little')
    respData = comport.read(respDataLen)
    comport.read(2) # ignore crc
    endbyte = int.from_bytes(comport.read(1))
    if (endbyte != 0x7e):
        print(f"invalid OemUsbWrite packet (invalid end byte) (got: 0x{endbyte:02X}, expected 0x7E)")
        return None
    lprint(f"returned data: {respData.hex()}")
    return respData

def NvGetString(index):
    comport.write(buildcmd((index).to_bytes(4, 'little'), RB_ID_NV_GETSTRING, RB_NV))
    return parseTkShell()

def NvSetString(index, text):
    comport.write(buildcmd(index.to_bytes(4, 'little') + text.encode() + "\0".encode(), RB_ID_NV_SETSTRING, RB_NV))

def NvGetInt(index):
    comport.write(buildcmd((index).to_bytes(4, 'little'), RB_ID_NV_GETINT, RB_NV))
    result = parseTkShell()
    if result == None:
        return None
    else:
        return int.from_bytes(result, "little")

def NvSetInt(index, value):
    comport.write(buildcmd(index.to_bytes(4, 'little') + value.to_bytes(4, 'little'), RB_ID_NV_SETINT, RB_NV))

def NvFlush():
    comport.write(buildcmd("".encode(), RB_ID_NV_FLUSH, RB_NV))

comport.port = waitForWave()
comport.open()

model = sendAT("AT+CGMM")

if model != "GT-S7230E" and not model.startswith("GT-S5230"):
    print("not a Samsung Wave 723 or Samsung Star!")
    exit()
print(f"model: {model}")
locksc = None
hasLockScreen = None
if model == "GT-S7230E":
    locksc = NvGetString(0x17C)
    hasLockScreen = NvGetInt(0x542)
else:
    locksc = NvGetString(0x12E)
    hasLockScreen = NvGetInt(0x4BF)
if locksc == None:
    exit()
else:
    print(f"has lockscreen set: {bool(hasLockScreen)}")
    print(f"lockscreen PIN: {locksc[4:len(locksc)].decode()}")