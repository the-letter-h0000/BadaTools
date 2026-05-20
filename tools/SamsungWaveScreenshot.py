import serial
import time
import sys
import re
import math
from PIL import Image

# Samsung Wave screenshotter
# data format:
# 22 [screen no] [chunk no (2 bytes LE)] 00 10 00 [rgb565 data] 00 00 00 00 00 [CRC-16/IBM-SDLC (2 bytes, LE)] 7E
# chunk formula:
#
# if (scr_x * scr_y < 384000):
#     math.ceil(scr_x * scr_y / 2048)
# else:
#     math.ceil(scr_x * scr_y / 4096)
#
# valid chk sizes: 2048, 4096
# chunk size choosing:
# 2048 if total pixels is less than 384,000 pixels
# 4096 if total pixels is more than 384,000 pixels

# TODO: check other Waves (only tested on a Samsung Wave 723 GT-S7230E (firmware: S723EPMKB1))

s = serial.Serial(sys.argv[1])

def sendcmd(cmd:str, sp):
    print(f"[d]: {cmd.strip()}")
    sp.write(cmd.encode()+b"\r\n")
    payload = b""
    time.sleep(0.07)
    while sp.in_waiting != 0:
        payload += sp.read(s.in_waiting)
        time.sleep(0.07)
    if payload.startswith(cmd.encode()):
        payload = payload[len(cmd)+2:]
    if payload.endswith(b"\r\nOK\r\n"):
        return payload[:-6].strip()
    else:
        return None

def sendcmd_until(cmd:str, utl, sp):
    print(f"[d]: {cmd.strip()}")
    sp.write(cmd.encode()+b"\r\n")
    payload = b""
    payload = sp.read_until(utl)
    if payload.startswith(cmd.encode()):
        payload = payload[len(cmd)+2:]
    if payload.endswith(b"\r\nOK\r\n"):
        return payload[:-6]
    else:
        return payload

def jail(h):
    i = 0
    res = bytearray()
    while i < len(h):
        if (i + 1 < len(h) and h[i] == 0x7D and h[i+1] == 0x5E):
            res.append(0x7E)
            i += 1
        elif (i + 1 < len(h) and h[i] == 0x7D and h[i+1] == 0x5D):
            res.append(0x7D)
            i += 1
        else:
            res.append(h[i])
        i += 1
    return res


if sendcmd("ATZ&FV1Q0E0S3=13S4=10S5=8+CREG=0+CGREG=0", s) == None:
    print("init not OK!!!")
    exit()

if sendcmd("AT+CGMI", s).decode().lower() != "samsung":
    print("not a samsung!!!")
    exit()

if len(sys.argv) != 3:
    scr = sendcmd("AT+LCDINFO", s)
    if scr == None:
        print("could not get screen info!!!")
        exit()
    
    scr_matches = re.search(r"LCDINFO: (\d*), (\d*)", scr.decode().strip())
    if not scr_matches:
        print(f"fatal regex error. (expected '+LCDINFO: x, y', got '{scr.decode().strip()}')")
        exit()
else:
    print("forced screen res")
    scr_matches = re.search(r"(\d*)x(\d*)", sys.argv[2])
    if not scr_matches:
        print(f"fatal regex error. (expected '123x456', got '{sys.argv[2]}')")
        exit()

scr_x = int(scr_matches.group(1))
scr_y = int(scr_matches.group(2))
print(f"SCREEN: {scr_x}x{scr_y}")
img = Image.new("RGB", (scr_x, scr_y))
print("created PIL Image")
if (scr_x * scr_y < 384000):
    chk_size = 2048
else:
    chk_size = 4096
print(f"chunk size: {chk_size}, total chunks needed: {math.ceil((scr_x * scr_y / chk_size))}")
print("prepare for screenshot...")
result = b""
print("starting screenshot...")
for i in range(0, math.ceil(scr_x * scr_y / chk_size)):
    s.reset_input_buffer()
    s.reset_output_buffer()
    payload = sendcmd_until(f"AT+GETDISPLAY=0,{i}", b"\x7e", s)
    if payload == None:
        print("what???")
        exit()
    if payload[0] != 0x22 or (payload[3] << 8 | payload[2]) != i:
        print(f"invalid header!!! (got {payload[0:7].hex(' ').upper()})")
        exit()
    result += jail(payload)[7:-8]
print("got framebuffer, converting from rgb565 to rgb888 (RGB)")
rgb888 = bytearray()
# experimental rgb565 parser
for i in range(0, len(result), 2):
    pix = (result[i+1] << 8) | result[i]
    r = (pix & 0b1111100000000000) >> 11
    g = (pix & 0b0000011111100000) >> 5
    b = pix & 0b0000000000011111
    # It Just Works(TM)
    rgb888.append((r << 3)|(r >> 2))
    rgb888.append((g << 2)|(g >> 4))
    rgb888.append((b << 3)|(b >> 2))
    # joe biden
img.frombytes(rgb888)
img.save(f"SamsungSWS_{round(time.time())}.png")
print(f"saved to SamsungSWS_{round(time.time())}.png")