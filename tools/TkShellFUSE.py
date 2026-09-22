import errno
import stat
import serial
import io
import datetime
import sys
import threading
import re

from fusepy import FUSE, FuseOSError, Operations

# TkShellFUSE.py - FUSE driver for FM operations on Samsung SHP Phones, replacing TkFileExplorer on Windows.
# currently read only

if len(sys.argv) < 3:
    print("not enough args. Required: mountPath serialPort [-h - show hidden files / folders]")
    print("examples:")
    print(f"python3 {sys.argv[0]} /mnt/wave /dev/ttyACM0 -h")
    print(f"python3 {sys.argv[0]} /mnt/wave /dev/ttyACM0")
    exit()

ack = bytes([0x7F, 0x01, 0x00, 0x42, 0x01, 0x7E])

comport = serial.Serial(sys.argv[2], 921600)

comport.timeout = 15

dirCache = {}
fileCache = {"path": "", "data": None}
handles = {}

lock = threading.RLock()

moveFilePadding = 0x304

RB_FM = 0x00
RB_ID_FM_OPENFILE = 0x00 #
RB_ID_FM_CLOSEFILE = 0x01 #
RB_ID_FM_READFILE = 0x02 #
RB_ID_FM_WRITEFILE = 0x03 #
RB_ID_FM_CREATEFILE = 0x04 #
RB_ID_FM_REMOVEFILE = 0x05 #
RB_ID_FM_MOVEFILE = 0x06 #
RB_ID_FM_GETFILEATTRIBUTES = 0x07
RB_ID_FM_OPENDIR = 0x08 #
RB_ID_FM_CLOSEDIR = 0x09 #
RB_ID_FM_READDIR = 0x0A #
RB_ID_FM_CREATEDIR = 0x0B #
RB_ID_FM_REMOVEDIR = 0x0C #

FM_READ =  0x00
FM_WRITE = 0x01 # overwrite bytes starting from offset 0 without clearing the file
FM_ERASE_WRITE = 0x09
FM_APPEND = 0x10

RB_ADM = 0x04
RB_ID_ADM_HELLO = 0x00
RB_ID_ADM_ECHO = 0x01

RB_MISC = 0x05
RB_ID_MISC_DEFAULT = 0x00

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
        comport.write(bytes([0x00])) # nudge it to send the payload instead of not responding, don't know why S5230's do that, do not remove.
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
            return None
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
        handle = openFile(path, FM_READ)
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

def createDirectory(path):
    print(f"[createDirectory] {path}")
    with lock:
        comport.write(buildcmd(path.encode() + "\0".encode(), RB_FM, RB_ID_FM_CREATEDIR))
        result = parseTkShell()
        if result == None:
            return None
        else:
            return int.from_bytes(result, "little") # 1 - success, 0 - the directory already exists

def removeDirectory(path):
    print(f"[removeDirectory] {path}")
    with lock:
        comport.write(buildcmd(path.encode() + "\0".encode(), RB_FM, RB_ID_FM_REMOVEDIR))
        result = parseTkShell()
        if result == None:
            return None
        else:
            return int.from_bytes(result, "little") # 1 - error, 0 - success

def removeFile(path):
    print(f"[removeFile] {path}")
    with lock:
        comport.write(buildcmd(path.encode() + "\0".encode(), RB_FM, RB_ID_FM_REMOVEFILE))
        result = parseTkShell()
        if result == None:
            return None
        else:
            return int.from_bytes(result, "little") # 1 - error, 0 - success

def moveFile(path, newPath):
    print(f"[moveFile] '{path}' -> '{newPath}'")
    with lock:
        comport.write(buildcmd(path.encode() + ("\0"*(moveFilePadding - len(path))).encode() + newPath.encode() + "\0".encode(), RB_FM, RB_ID_FM_MOVEFILE))
        result = parseTkShell()
        if result == None:
            return None
        else:
            return int.from_bytes(result, "little") # 1 - success

def createFile(path:str, mode:int):
    print(f"[createFile] '{path}' mode: {mode}")
    with lock:
        comport.write(buildcmd(mode.to_bytes(4, "little") + path.encode() + "\0".encode(), RB_FM, RB_ID_FM_CREATEFILE))
        result = parseTkShell()
        if result == None:
            return None
        else:
            return int.from_bytes(result, "little") # retuns an hFile to created file

def writeFile(hFile:int, bufLen:int, buffer):
    print(f"[writeFile] hFile: {hFile:08X} bufLen: {bufLen}")
    with lock:
        comport.write(buildcmd(hFile.to_bytes(4, "little") + bufLen.to_bytes(4, "little") + buffer, RB_FM, RB_ID_FM_WRITEFILE))
        result = parseTkShell()
        if result == None:
            return None
        else:
            return int.from_bytes(result, "little") # 1 - success

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
        "attrib": 0,
        "month": 0,
        "day": 0,
        "hour": 0,
        "minute": 0,
        "second": 0,
    }
    entryType = int.from_bytes(f.read(4), "little")
    filesize = int.from_bytes(f.read(4), "little")
    attrib = int.from_bytes(f.read(4), "little")
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
        "attrib": attrib,
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
        if len(result) < 4 or int.from_bytes(result[:4], "little") != 1:
            return {}
        if result[4:].split("\0".encode(), 1)[0].decode(errors='ignore') != "Hello, TkShell~":
            return False
        return True

def clearFileCache():
    print(f"[clearFileCache] clear file cache")
    fileCache["data"] = None
    fileCache["path"] = ""

def getDevConInfo():
    with lock:
        comport.write(buildcmd("DevConInfo\0".encode(), RB_MISC, RB_ID_MISC_DEFAULT))
        result = parseTkShell()
        parsed = {}
        if result == None:
            return parsed
        if len(result) < 4 or int.from_bytes(result[:4], "little") != 1:
            return parsed
        data = result[4:].decode(errors="ignore")
        items = data.split(';')
        for item in items:
            match = re.search(r"(.*)\((.*)\)", item)
            if match != None:
                parsed[match.group(1)] = match.group(2)
        return parsed

def setFmSecureMode(mode):
    with lock:
        if mode == True:
            comport.write(buildcmd("FmSecureMode on\0".encode(), RB_MISC, RB_ID_MISC_DEFAULT))
        else:
            comport.write(buildcmd("FmSecureMode off\0".encode(), RB_MISC, RB_ID_MISC_DEFAULT))
        result = parseTkShell()
        if result == None:
            return False
        if len(result) < 4 or int.from_bytes(result[:4], "little") != 8:
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

device = getDevConInfo()
if device == {} or device["MN"].startswith("GT-S5230"):
    print("S5230 detected.")
    moveFilePadding = 0x12C

if device != {}:
    print("Device info:")
    for prop, val in device.items():
        print(f"{prop}: {val}")

if len(sys.argv) > 3 and sys.argv[3] == "-h":
    if not setFmSecureMode(False):
        printW("failed to set FmSecureMode")
else:
    if not setFmSecureMode(True):
        printW("failed to set FmSecureMode")

class TkShellFS(Operations):
    def getattr(self, path:str, fh=None):
        print(f"[FUSE] getattr path:{path}")
        if path == "/":
            return {
                "st_mode": stat.S_IFDIR | 0o777,
                "st_nlink": 2
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
                        "st_mode": stat.S_IFDIR | 0o777,
                        "st_nlink": 2,
                        "st_mtime": dt,
                        "st_atime": dt,
                        "st_ctime": dt
                    }
                else:
                    return {
                        "st_mode": stat.S_IFREG | 0o777,
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
            if entry["name"] == None:
                printW("[FUSE] raising errno.EIO!")
                raise FuseOSError(errno.EIO)
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

    def mkdir(self, path, mode):
        print(f"[FUSE] mkdir {path}")
        result = createDirectory(path)
        if result == None:
            printW("[FUSE] raising errno.EIO!")
            raise FuseOSError(errno.EIO)
        if result == 0:
            printW("[FUSE] raising errno.EEXIST!")
            raise FuseOSError(errno.EEXIST)
        dirCache.clear()
        return 0
    
    def rmdir(self, path):
        print(f"[FUSE] rmdir {path}")
        result = removeDirectory(path)
        if result == None:
            printW("[FUSE] raising errno.EIO! (error parsing)")
            raise FuseOSError(errno.EIO)
        if result != 1:
            printW(f"[FUSE] raising errno.EIO! (device returned {result})")
            raise FuseOSError(errno.EIO)
        dirCache.clear()
        return 0

    def write(self, path, data, offset, fh):
        print(f"[FUSE] write '{path}' {offset}")
        clearFileCache()
        readResult = readFullFile(path)
        if readResult == None:
            printW("[FUSE] raising errno.EIO! (readFullFile returned None)")
            raise FuseOSError(errno.EIO)

        readResult = bytearray(readResult)

        if offset > len(readResult):
            readResult.extend(("\0".encode()) * (offset - len(readResult)))

        readResult[offset:offset + len(data)] = data
        hFile = createFile(path, FM_ERASE_WRITE)
        if hFile == 0xFFFFFFFF:
            printW(f"[FUSE] raising errno.EIO! (hFile is -1)")
            raise FuseOSError(errno.EIO)
        
        result = writeFile(hFile, len(readResult), readResult)
        closeFile(hFile)
        if result == None:
            printW("[FUSE] raising errno.EIO! (error writing)")
            raise FuseOSError(errno.EIO)
        if result != 1:
            printW(f"[FUSE] raising errno.EIO! (write) (device returned {result})")
            raise FuseOSError(errno.EIO)
        return len(data)

    def unlink(self, path):
        print(f"[FUSE] unlink {path}")
        clearFileCache()
        dirCache.clear()

        result = removeFile(path)
        if result == None:
            printW("[FUSE] raising errno.EIO!")
            raise FuseOSError(errno.EIO)
        if result != 1:
            printW(f"[FUSE] raising errno.EIO! (device returned {result})")
            raise FuseOSError(errno.EIO)
        return 0

    def rename(self, old, new):
        print(f"[FUSE] rename '{old}' -> '{new}'")
        clearFileCache()
        dirCache.clear()

        result = moveFile(old, new)
        if result == None:
            printW("[FUSE] raising errno.EIO!")
            raise FuseOSError(errno.EIO)
        if result != 1:
            printW(f"[FUSE] raising errno.EIO! (device returned {result})")
            raise FuseOSError(errno.EIO)
        return 0

    def create(self, path, mode, fi=None):
        print(f"[FUSE] create {path}")
        hFile = createFile(path, FM_ERASE_WRITE)
        if hFile == 0xFFFFFFFF:
            printW(f"[FUSE] raising errno.EIO! (hFile is -1)")
            raise FuseOSError(errno.EIO)
        closeFile(hFile)

        clearFileCache()
        dirCache.clear()
        return 0

FUSE(TkShellFS(), sys.argv[1], foreground=True, ro=False)
