import sys
import serial
import time

def crc16_ibm_sdlc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0x8408 if crc & 1 else crc >> 1
    return crc ^ 0xFFFF

def sendcmd(cmd, sp):
    sp.write(cmd)
    payload = b""
    time.sleep(0.10)
    while sp.in_waiting != 0:
        payload += sp.read(sp.in_waiting)
        time.sleep(0.10)
    return payload

def escape(barr):
    res = bytearray()
    for b in barr:
        if b == 0x7E:
            res.append(0x7D)
            res.append(0x5E)
        elif b == 0x7D:
            res.append(0x7D)
            res.append(0x5D)
        else:
            res.append(b)
    return res

something = 0

s = serial.Serial(sys.argv[1])
s.timeout = 1

while True:
    rawtext = input(">> ")
    if rawtext.startswith("exit"):
        break

    COMMAND = bytes.fromhex(rawtext)

    crc = crc16_ibm_sdlc(bytes(COMMAND)).to_bytes(2, "little")

    result = bytearray()
    result.append(0x7E)
    result.append(something)
    result.extend(escape(COMMAND))
    result.extend(escape(crc))
    result.append(0x7E)
    cmd_result = sendcmd(result, s)
    print(f"sent to device: {result.hex()}")
    something = (something + 1) & 3
    print("output:")
    print(cmd_result.hex())