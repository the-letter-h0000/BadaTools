import errno
import stat
import serial
import io
import datetime
import sys
import threading

from fusepy import FUSE, FuseOSError, Operations

# TkShellFUSE.py - FUSE driver for FM operations on Samsung SHP Phones, replacing TkFileExplorer on Windows.
# currently read only

if len(sys.argv) < 3:
    print("not enough args. Required: mountPath serialPort")
    exit()

ack = bytes([0x7F, 0x01, 0x00, 0x42, 0x01, 0x7E])

comport = serial.Serial(sys.argv[2], 921600)

dirCache = {}
fileCache = {"path": "", "data": None}

lock = threading.RLock()

RB_FM = 0x00
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

RB_ADM = 0x04
RB_ID_ADM_HELLO = 0x00
RB_ID_ADM_ECHO = 0x01

def printW(text):
    print(f"\x1b[1;38;2;255;255;0m{text}\x1b[0m")

def crc16_cms(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            crc = (crc << 1) ^ 0x8005 if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return crc

def buildcmd(data, command, subcommand):
    crc = crc16_cms(bytes([subcommand]) + bytes([command]) + len(data).to_bytes(2, 'little') + data)
    packet = bytearray()
    packet.append(0x7F)
    packet.extend((len(data)+6).to_bytes(2, 'little'))
    packet.append(0x42)
    packet.append(subcommand) # originally a 16-bit ushort (0xAABB (AA - command, BB - subcommand))
    packet.append(command)
    packet.extend(len(data).to_bytes(2, 'little'))
    packet.extend(data)
    packet.extend(crc.to_bytes(2, 'big'))
    packet.append(0x7E)
    #print(f"[buildcmd] sent: {packet.hex()}")
    return packet

def parseTkShell():
    with lock:
        i = 0
        while (i < len(ack)):
            b = int.from_bytes(comport.read(1))
            if b == ack[i]:
                i += 1
            else:
                if b == ack[0]:
                    i = 1
                else:
                    i = 0

        st = int.from_bytes(comport.read(1))
        if (st != 0x7f):
            printW(f"invalid OemUsbWrite packet (invalid start byte) (got: 0x{st:02X}, expected 0x7F)")
            return None
        comport.read(2), 'little' # ignore packet size
        B_thing = int.from_bytes(comport.read(1))
        if (B_thing != 0x42):
            printW(f"invalid OemUsbWrite packet (invalid byte) (got: 0x{B_thing:02X}, expected 0x42)")
            return None
        subc = comport.read(1)
        cmd = comport.read(1)
        respDataLen = int.from_bytes(comport.read(2), 'little')
        respData = comport.read(respDataLen)
        crc = int.from_bytes(comport.read(2), "big") # CRC is already Little Endian when calculated with crc16_cms
        endbyte = int.from_bytes(comport.read(1))
        if (endbyte != 0x7e):
            printW(f"invalid OemUsbWrite packet (invalid end byte) (got: 0x{endbyte:02X}, expected 0x7E)")
            return None
        crcCalc = crc16_cms(subc + cmd + len(respData).to_bytes(2, 'little') + respData)
        if crc != crcCalc:
            printW(f"CRC mismatch!")
            return None
        #print(f"returned data payload: {respData.hex()}")
        return respData

def openDirectory(path:str):
    print(f"[openDirectory] {path}")
    with lock:
        comport.write(buildcmd(path.encode() + "\0".encode(), RB_FM, RB_ID_FM_OPENDIR))
        result = parseTkShell()
        if result == None:
            return 0xFFFFFFFF
        else:
            hDir = int.from_bytes(result, 'little')
            if hDir == 0xFFFFFFFF: # no free handles, or file / directory does not exist
                printW("no free hDir handles, or file / directory does not exist")
            return hDir

def closeDirectory(hDir:int):
    print(f"[closeDirectory] hDir: {hDir:08X}")
    with lock:
        comport.write(buildcmd(hDir.to_bytes(4, "little"), RB_FM, RB_ID_FM_CLOSEDIR))
        result = parseTkShell()
        if result == None:
            return -1
        else:
            return int.from_bytes(result, "little")

def openFile(path:str, mode:int):
    print(f"[openFile] '{path}' mode: {mode}")
    with lock:
        comport.write(buildcmd(mode.to_bytes(4, "little") + path.encode() + "\0".encode(), RB_FM, RB_ID_FM_OPENFILE))
        result = parseTkShell()
        if result == None:
            return 0xFFFFFFFF
        else:
            hFile = int.from_bytes(result, "little")
            if hFile == 0xFFFFFFFF:
                printW("no free hFile handles, or file / directory does not exist")
            return hFile

def closeFile(hFile:int):
    print(f"[closeFile] hFile: {hFile:08X}")
    with lock:
        comport.write(buildcmd(hFile.to_bytes(4, "little"), RB_FM, RB_ID_FM_CLOSEFILE))
        result = parseTkShell()
        if result == None:
            return -1
        else:
            return int.from_bytes(result, "little")

def readFile(hFile:int, length:int):
    print(f"[readFile] hFile: {hFile:08X} len: {length}")
    with lock:
        comport.write(buildcmd(hFile.to_bytes(4, "little") + length.to_bytes(4, "little"), RB_FM, RB_ID_FM_READFILE))
        result = parseTkShell()
        return result

def readFullFile(path):
    print(f"[readFullFile] {path}")
    with lock:
        handle = openFile(path, 2)
        if handle == 0xFFFFFFFF:
            return None
        result = bytearray()
        while True:
            readResult = readFile(handle, 4000)
            pack = io.BytesIO(readResult)
            if int.from_bytes(pack.read(4), "little") != 1:
                closeFile(handle)
                return bytes(result)
            size = int.from_bytes(pack.read(4), "little")
            if size == 0:
                closeFile(handle)
                return bytes(result)
            else:
                result.extend(pack.read(size))

def readDirEntry(hDir:int):
    print(f"[readDirEntry] hDir: {hDir:08X}")
    with lock:
        comport.write(buildcmd(hDir.to_bytes(4, "little"), RB_FM, RB_ID_FM_READDIR))
        result = parseTkShell()
        return result

def parseFmOpenEntry(entry:bytes):
    f = io.BytesIO(entry)
    isvalid = int.from_bytes(f.read(4), "little") # should be always 1, except when the end of the directory has been reached
    if isvalid != 1:
        print(f"[parseFmOpenEntry] (isvalid != 1) {isvalid}")
        return {
        "isValid": isvalid,
        "entryType": 0,
        "year": 0,
        "name": "",
        "filesize": 0,
        "unk2": 0,
        "month": 0,
        "day": 0,
        "hour": 0,
        "minute": 0,
        "second": 0,
    }
    entryType = int.from_bytes(f.read(4), "little")
    filesize = int.from_bytes(f.read(4), "little")
    unk2 = int.from_bytes(f.read(4), "little")
    year = int.from_bytes(f.read(4), "little")
    month = int.from_bytes(f.read(4), "little")
    day = int.from_bytes(f.read(4), "little")
    hour = int.from_bytes(f.read(4), "little")
    minute = int.from_bytes(f.read(4), "little")
    second = int.from_bytes(f.read(4), "little")
    name = f.read(0x100).split("\0".encode(), 1)[0].decode(errors='ignore')
    result = {
        "isValid": isvalid,
        "entryType": entryType,
        "year": year,
        "name": name,
        "filesize": filesize,
        "unk2": unk2,
        "month": month, # date modified
        "day": day,
        "hour": hour,
        "minute": minute,
        "second": second,
    }
    #print(f"[parseFmOpenEntry] {result}")
    return result

def getDirectory(path):
    print(f"[getDirectory] {path}")
    with lock:
        handle = openDirectory(path)
        result = []
        if handle == 0xFFFFFFFF:
            return None
        while True:
            meta = readDirEntry(handle)
            if meta == None:
                closeDirectory(handle)
                return None
            parsed = parseFmOpenEntry(meta)
            if parsed["isValid"] != 1:
                break
            result.append(parsed)
        closeDirectory(handle)
        return result

def getCachedDirectory(path):
    with lock:
        if len(dirCache) > 1200:
            dirCache.clear()
        if path not in dirCache:
            print(f"[getCachedDirectory] {path} is NOT cached")
            dirCache[path] = getDirectory(path)
        return dirCache[path]

def readCachedFile(path):
    with lock:
        if fileCache["path"] != path:
            print("[readCachedFile] request to read from uncached file")
            fileCache["data"] = readFullFile(path)
            fileCache["path"] = path
        return fileCache["data"]

def ifAlive():
    with lock:
        comport.write(buildcmd("".encode(), RB_ADM, RB_ID_ADM_HELLO))
        result = parseTkShell()
        if result == None:
            return False
        if result[4:].split("\0".encode(), 1)[0].decode(errors='ignore') != "Hello, TkShell~":
            return False
        return True

# ===================================
# MAIN PROGRAM STARTS HERE
# ===================================

if not ifAlive():
    printW("the device does not support TkShell or is not a Samsung.")
    exit()
else:
    print(f"success getting hello command, connected to {comport.name} @ {comport.baudrate} baud")

class MyFS(Operations):
    def getattr(self, path:str, fh=None):
        print(f"[FUSE] getattr path:{path}")
        if path == "/":
            return {
                "st_mode": stat.S_IFDIR | 0o755,
                "st_nlink": 2,
            }
        parentDir = path.rsplit("/", 1)
        name = parentDir[1]
        if parentDir[0] == "":
            parentDir[0] = "/"
        entries = getCachedDirectory(parentDir[0])
        if entries == None:
            printW("[FUSE] raising errno.EIO!")
            raise FuseOSError(errno.EIO)
        for entry in entries:
            if entry["name"] == name:
                dt = datetime.datetime(entry["year"], entry["month"], entry["day"], entry["hour"], entry["minute"], entry["second"]).timestamp()
                if entry["entryType"] == 2:
                    return {
                        "st_mode": stat.S_IFDIR | 0o755,
                        "st_nlink": 2,
                        "st_mtime": dt,
                        "st_atime": dt,
                        "st_ctime": dt
                    }
                else:
                    return {
                        "st_mode": stat.S_IFREG | 0o444,
                        "st_nlink": 1,
                        "st_size": entry["filesize"],
                        "st_mtime": dt,
                        "st_atime": dt,
                        "st_ctime": dt
                    }
        raise FuseOSError(errno.ENOENT)

    def readdir(self, path, fh):
        print(f"[FUSE] readdir path:{path}")
        entries = getCachedDirectory(path)
        result = []
        for entry in entries:
            result.append(entry["name"])
        return result

    def open(self, path, flags):
        return 0

    def read(self, path, size, offset, fh):
        print(f"[FUSE] read file:{path}")
        data = readCachedFile(path)
        if data == None:
            printW("[FUSE] raising errno.EIO!")
            raise FuseOSError(errno.EIO)
        return data[offset:offset + size]


FUSE(MyFS(), sys.argv[1], foreground=True, ro=True)