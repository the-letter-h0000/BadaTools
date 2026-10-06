import io
import sys
from PIL import Image

# SamsungRC2imageExtractor.py - extract resources embedded in rc2 files of Samsung firmware files
# tested only on:
# S7230EXEKF1 - Rsrc2_S7230E(Low).rc2
# S5230XXIG2  - Rsrc2_S5230(Low).rc2
# S5230ZLJA3  - Rsrc2_S5230_Taiwan(Low).rc2
# S5230ZLJA3  - Rsrc2_S5230_Taiwan(Mid).rc2

metadataHeader = b"\x5D\x5C\x5B\x5A" # required by Boot2, otherwise display blue screen or other (memset)
infoHeader = b"\xAB\xCD\xAB\xCD"
debugLevels = ["Low", "Mid", "High"]

if (len(sys.argv) < 2):
    print("file path required")
    exit()

rc2 = io.FileIO(sys.argv[1])

def findMtDHead():
    buffer = bytearray()
    while True:
        b = rc2.read(1)
        if len(b) == 0:
            print("cannot find signature")
            exit()
        buffer += b
        if len(buffer) > len(metadataHeader):
            buffer.pop(0)
        if buffer == metadataHeader:
            return rc2.tell() - len(metadataHeader)

def findRc2Head():
    buffer = bytearray()
    rc2.seek(0, 2)
    rc2.seek(-1, 1)
    while True:
        b = rc2.read(1)
        if len(b) == 0:
            print("cannot find signature")
            exit()
        buffer += b
        if len(buffer) > len(infoHeader):
            buffer.pop(0)
        if buffer == infoHeader:
            return rc2.tell() - len(infoHeader)
        rc2.seek(-2, 1)

def parseRc2Metadata():
    result = {}
    result["splashScrAddr"] = int.from_bytes(rc2.read(4), "little")
    result["splashScrSize"] = int.from_bytes(rc2.read(4), "little")
    rc2.seek(24, 1)
    result["splashXRes"] = int.from_bytes(rc2.read(4), "little")
    result["splashYRes"] = int.from_bytes(rc2.read(4), "little")
    rc2.seek(0x63C, 1)
    result["chargeScrAddr"] = int.from_bytes(rc2.read(4), "little")
    result["chargeScrSize"] = int.from_bytes(rc2.read(4), "little")
    rc2.seek(0x204, 1)
    result["misc1ScrAddr"] = int.from_bytes(rc2.read(4), "little")
    result["misc1ScrSize"] = int.from_bytes(rc2.read(4), "little")
    rc2.seek(12, 1)
    result["misc1XRes"] = int.from_bytes(rc2.read(4), "little")
    result["misc1YRes"] = int.from_bytes(rc2.read(4), "little")
    result["misc2ScrAddr"] = int.from_bytes(rc2.read(4), "little")
    result["misc2ScrSize"] = int.from_bytes(rc2.read(4), "little")
    rc2.seek(12, 1)
    result["misc2XRes"] = int.from_bytes(rc2.read(4), "little")
    result["misc2YRes"] = int.from_bytes(rc2.read(4), "little")
    return result

def FromRgb565(offset, length):
    # experimental rgb565 parser
    print(f"read {length} bytes of rgb565 from 0x{offset:08X}")
    rc2.seek(offset)
    result = rc2.read(length)
    rgb888 = bytearray()
    for i in range(0, len(result), 2):
        pix = (result[i+1] << 8) | result[i]
        r = (pix & 0b1111100000000000) >> 11
        g = (pix & 0b0000011111100000) >> 5
        b = pix & 0b0000000000011111
        # It Just Works(TM)
        rgb888.append((r << 3)|(r >> 2))
        rgb888.append((g << 2)|(g >> 4))
        rgb888.append((b << 3)|(b >> 2))
    return rgb888

rc2.seek(8) # go to debug level
dlevel = int.from_bytes(rc2.read(4), "little")
if dlevel < len(debugLevels):
    print(f"Debug level: {debugLevels[dlevel]} ({dlevel})")
else:
    print(f"Debug level: Unknown ({dlevel})")
rc2.seek(0x10) # go to DEF header
if (rc2.read(3).decode(errors="ignore") != "DEF"):
    print("warning: no DEF found")

foundBase = findMtDHead()
base = int.from_bytes(rc2.read(4), "little")
while foundBase != base:
    foundBase = findMtDHead()
    base = int.from_bytes(rc2.read(4), "little")

print(f"found metadata header at 0x{foundBase:08X}")
# tell() is now after the signature and base address
parsed = parseRc2Metadata()
if (parsed["splashScrAddr"] == 0xFFFFFFFF): # something's seriously wrong
    print("invalid or corrupted rc2")
    exit()

skipMisc = False
splash = Image.new("RGB", (parsed["splashXRes"], parsed["splashYRes"]))
charger = Image.new("RGB", (parsed["splashXRes"], parsed["splashYRes"]))
misc1 = None
misc2 = None
if (parsed["misc1ScrAddr"] == 0xFFFFFFFF and parsed["misc1YRes"] == 0xFFFFFFFF and parsed["misc2ScrAddr"] == 0xFFFFFFFF and parsed["misc2YRes"] == 0xFFFFFFFF):
    print("skip misc")
    skipMisc = True

if not skipMisc:
    misc1 = Image.new("RGB", (parsed["misc1XRes"], parsed["misc1YRes"]))
    misc2 = Image.new("RGB", (parsed["misc2XRes"], parsed["misc2YRes"]))

if ((parsed["splashXRes"] * parsed["splashYRes"]) * 2 != parsed["splashScrSize"]):
    print("boot splash screen: size mismatch!")
else:
    splash.frombytes(FromRgb565(parsed["splashScrAddr"], parsed["splashScrSize"]))

if ((parsed["splashXRes"] * parsed["splashYRes"]) * 2 != parsed["chargeScrSize"]):
    print("initial charging screen: size mismatch!")
else:
    charger.frombytes(FromRgb565(parsed["chargeScrAddr"], parsed["chargeScrSize"]))

if not skipMisc:
    if ((parsed["misc1XRes"] * parsed["misc1YRes"]) * 2 != parsed["misc1ScrSize"]):
        print("misc 1: size mismatch!")
    else:
        misc1.frombytes(FromRgb565(parsed["misc1ScrAddr"], parsed["misc1ScrSize"]))

    if ((parsed["misc2XRes"] * parsed["misc2YRes"]) * 2 != parsed["misc2ScrSize"]):
        print("misc 2: size mismatch!")
    else:
        misc2.frombytes(FromRgb565(parsed["misc2ScrAddr"], parsed["misc2ScrSize"]))

splash.save(f"{sys.argv[1].replace(".","_")}_boot_splash.png")
charger.save(f"{sys.argv[1].replace(".","_")}_charge_splash.png")
if not skipMisc:
    misc1.save(f"{sys.argv[1].replace(".","_")}_misc1.png")
    misc2.save(f"{sys.argv[1].replace(".","_")}_misc2.png")

print("saved")
print("RC2 info:")
findRc2Head() # seek to 2nd byte of sign
rc2.seek(3, 1) # skip the rest
print(f"base in flash: 0x{int.from_bytes(rc2.read(4), "little"):08X}")
print(f"something: 0x{int.from_bytes(rc2.read(4), "little"):08X}")
print(f"model: {rc2.read(20).split("\0".encode(), 1)[0].decode(errors='ignore')}")