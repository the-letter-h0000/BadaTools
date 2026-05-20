import serial
import sys
import time
import io
import os

# for use with Samsung phones running SHP (e.g. S5230, S7230E, etc) and in Upload Mode

# source:
# void UploadModeParseCommand(int command) in uncompress_boot2.bin, 0x0005d2e8
# {
#   astruct_1 *paVar1;
#   undefined4 uVar2;
#   int iVar3;
#   uint startAddr;
#   char *pcVar4;
#   uint uVar5;
#   int iVar6;
#   undefined4 uVar7;
#   int iVar8;
#   uint uVar9;
#   int local_58;
#   char dataxfer_chunk1 [4];
#   char dataxfer_chunk2 [4];
#   char dataxfer_chunk3 [4];
#   char powerdown_chunk1 [4];
#   char powerdown_chunk2 [4];
#   char powerdown_chunk3 [4];
#   char postamble_chunk1 [4];
#   char postamble_chunk2 [4];
#   char postamble_chunk3 [4];
#   char acknowledgment_chunk1 [4];
#   char acknowledgment_chunk2 [4];
#   char acknowledgment_chunk3 [4];
#   char acknowledgment_chunk4 [4];
#   char preamble_chunk1 [4];
#   char preamble_chunk2 [4];
#   char preamble_chunk3 [4];
#   
#   preamble_chunk1 = (char  [4])s_PrEaMbLe_0005d4b8._0_4_;
#   preamble_chunk2 = (char  [4])s_PrEaMbLe_0005d4b8._4_4_;
#   preamble_chunk3 = (char  [4])s_PrEaMbLe_0005d4b8._8_4_;
#   acknowledgment_chunk1 = (char  [4])s_AcKnOwLeDgMeNt_0005d4c4._0_4_;
#   acknowledgment_chunk2 = (char  [4])s_AcKnOwLeDgMeNt_0005d4c4._4_4_;
#   acknowledgment_chunk3 = (char  [4])s_AcKnOwLeDgMeNt_0005d4c4._8_4_;
#   acknowledgment_chunk4 = (char  [4])s_AcKnOwLeDgMeNt_0005d4c4._12_4_;
#   postamble_chunk1 = (char  [4])s_PoStAmBlE_0005d4d4._0_4_;
#   postamble_chunk2 = (char  [4])s_PoStAmBlE_0005d4d4._4_4_;
#   postamble_chunk3 = (char  [4])s_PoStAmBlE_0005d4d4._8_4_;
#   powerdown_chunk1 = (char  [4])s_PoWeRdOwN_0005d4e0._0_4_;
#   powerdown_chunk2 = (char  [4])s_PoWeRdOwN_0005d4e0._4_4_;
#   powerdown_chunk3 = (char  [4])s_PoWeRdOwN_0005d4e0._8_4_;
#   dataxfer_chunk1 = (char  [4])s_DaTaXfEr_0005d4ec._0_4_;
#   dataxfer_chunk2 = (char  [4])s_DaTaXfEr_0005d4ec._4_4_;
#   dataxfer_chunk3 = (char  [4])s_DaTaXfEr_0005d4ec._8_4_;
#   iVar3 = strcmp(command,powerdown_chunk1);
#   if (iVar3 == 0) {
#     do {
#                     /* WARNING: Do nothing block with infinite loop */
#     } while( true );
#   }
#   iVar3 = strcmp(command,preamble_chunk1);
#   paVar1 = 841E6D40;
#   if (iVar3 == 0) {
#     iVar3 = 1;
#   }
#   else {
#     if (((841E6D40->mode != 1) && (841E6D40->mode != 2)) || (iVar3 = strlen(command), iVar3 != 8)) {
#       if ((paVar1->mode != 3) ||
#          ((iVar3 = strcmp(command,dataxfer_chunk1), iVar3 != 0 &&
#           (iVar3 = strcmp(command,acknowledgment_chunk1), iVar3 != 0)))) {
#         paVar1->mode = 0;
#         return;
#       }
#       iVar3 = 841F6DC0;
#       startAddr = paVar1->startAddr;
#       if ((startAddr == 01FFFFFC) && (paVar1->endAddr == startAddr + 3)) { // return 3 LE values: [BuildInfoAddr] 0x12345678 0xyyyyyyyy
#         uVar7 = 0xc;
#         *(undefined4 *)(841F6DC0 + 0x40) = *8FF00004;
#         uVar2 = 12345678;
#         *(undefined4 *)(iVar3 + 0x48) = 0xb0000000;
#         *(undefined4 *)(iVar3 + 0x44) = uVar2;
#       }
#       else {
#         if ((startAddr == 03FFFFFC) && (paVar1->endAddr == startAddr + 3)) {
#           rebootDevice();
#           return;
#         }
#         if ((startAddr != 01EEEFFC) || (paVar1->endAddr != startAddr + 3)) { // return size of the flash dump (FSR_BML_GetDumpSize)
#           if (startAddr <= paVar1->endAddr) {
#             iVar8 = paVar1->endAddr - startAddr;
#             iVar3 = 0x40000;
#             if (iVar8 + 1U < 0x40001) {
#               iVar3 = iVar8 + 1;
#             }
#             local_58 = iVar3;
#             if ((startAddr < 0xb0000000) || (paVar1->field64_0x4c + 0xb0000000U <= startAddr)) {
#               if (startAddr + 0x60000000 < 12500000) {
#                 if (startAddr == 12500000 * 0x200) {
#                   FUN_000179ac(&841E6D40->field8_0x8);
#                   paVar1->field8_0x8 = 0;
#                 }
#                 FUN_0005d848(841F6DC0 + 0x40,paVar1->startAddr + 0x50000000,iVar3,&local_58);
#               }
#               else {
#                 if (startAddr < 0xf0000000) goto LAB_0005d49a;
#                 FUN_0005d550(841F6DC0 + 0x40,startAddr & 0xfffffff,iVar3);
#               }
#             }
#             else {
#               FUN_0005d774(841F6DC0 + 0x40,startAddr + 0x50000000,iVar3,&local_58);
#             }
#             startAddr = 841F6DC0 + 0x40;
# LAB_0005d49a:
#             writeOut(startAddr,local_58);
#             paVar1->startAddr = paVar1->startAddr + local_58;
#             return;
#           }
#           uVar7 = 10;
#           pcVar4 = postamble_chunk1;
#           paVar1->mode = 0;
#           goto LAB_0005d4ae;
#         }
#         FUN_00017c5c(0);
#         FUN_0005de98(&841E6D40->field64_0x4c);
#         uVar7 = 4;
#         *(int *)(iVar3 + 0x40) = paVar1->field64_0x4c;
#       }
#       pcVar4 = (char *)(841F6DC0 + 0x40);
#       goto LAB_0005d4ae;
#     }
#     iVar8 = 1;
#     startAddr = 0;
#     iVar3 = 8;
#     do {
#       uVar5 = (uint)*(byte *)(command + iVar3 + -1);
#       uVar9 = uVar5 - 0x30;
#       if (9 < uVar9) {
#         if (uVar5 - 0x61 < 0x1a) {
#           uVar9 = uVar5 - 0x57;
#         }
#         else {
#           uVar9 = uVar5 - 0x37;
#         }
#       }
#       iVar6 = iVar8 * uVar9;
#       iVar8 = iVar8 << 4;
#       startAddr = iVar6 + startAddr;
#       iVar3 = iVar3 + -1;
#     } while (iVar3 != 0);
#     if (paVar1->mode == 1) {
#       iVar3 = 2;
#       paVar1->startAddr = startAddr;
#     }
#     else {
#       iVar3 = 3;
#       paVar1->endAddr = startAddr;
#     }
#   }
#   paVar1->mode = iVar3;
#   uVar7 = 0xf;
#   pcVar4 = acknowledgment_chunk1;
# LAB_0005d4ae:
#   writeOut(pcVar4,uVar7);
#   return;
# }

# TODO: check other devices (only tested on a Samsung Wave 723 GT-S7230E (firmware: S723EPMKB1))

def sendcmd(command, serial):
    #print(f"[d] send {command}")
    serial.reset_input_buffer() # rename to magic_ttyACM_fixer_9000(), fixes like 90% of problems, i don't know why, and neither god knows
    serial.write(command.encode().ljust(12, b'\x00'))
    b = serial.read_until(b'\0')
    if b"AcKnOwLeDgMeNt" in b:
        #print("recv AcKnOwLeDgMeNt")
        return True
    else:
        print("not ACK")
        #print(b)
        return False

# i'm sorry. (i vibecoded this function)
def is_valid_8char_hex(s):
    try:
        # Check if it's exactly 8 chars
        if len(s) != 8:
            return False
        # Try to convert to int using base 16
        int(s, 16)
        return True
    except (ValueError, TypeError):
        return False

def dumpmem(start, end, s):
    if sendcmd("PrEaMbLe", s) == False:
        print("FAIL AT: preamble")
        return None
    if sendcmd(f"{start:08X}", s) == False:
        print("FAIL AT: start addr")
        return None
    if sendcmd(f"{end:08X}", s) == False:
        print("FAIL AT: end addr")
        return None
    s.write("DaTaXfEr".encode().ljust(12, b'\x00'))
    if end - start == 3 and (start == 0x01FFFFFC or start == 0x03FFFFFC or start == 0x01EEEFFC):
        time.sleep(0.1)
        return s.read_all()
    else:
        data = s.read(end - start)
        if len(data) < end - start:
            data += b"\x00"*((end - start) - len(data))
        return data

def showhelp():
    print(f"{sys.argv[0]} - dump RAM from Samsung SHP phones in Upload mode")
    print("usage:")
    print(f"{sys.argv[0]} <serialport> <command> [args]")
    print((" "*4)+"args:")
    print((" "*8)+"<serialport> - your serial port (e.g. /dev/ttyACM0, COM0, etc)")
    print((" "*4)+"commands:")
    print((" "*8)+"help                       - show this screen")
    print((" "*8)+"getinfo                    - get firmware info")
    print((" "*8)+"getcrash                   - get bluescreen details")
    print((" "*8)+"nandsize                   - get NAND size")
    print((" "*8)+"sendraw [CMD1] [CMD2] ...  - send raw commands to bootloader on device")
    print((" "*8)+"halt                       - halt bootloader on device")
    print((" "*8)+"reboot                     - restarts device")
    print((" "*8)+"<start> <end> <output>     - dump ram from <start> to <end>\n(both must be 8 char hex!) ('-' as <output> will dump to stdout)")

def sizehelper(size):
    if size < 1024:
        return [size, "bytes"]
    elif size < 1024*1024:
        return [size/1024, "KiB"]
    elif size < 1024*1024*1024:
        return [size/1024/1024, "MiB"]
    elif size < 1024*1024*1024*1024:
        return [size/1024/1024/1024, "GiB"]
    else:
        return [size, "bytes"]
    
def parseCallstack(stack):
    result = []
    stream = io.BytesIO(stack)
    func = "joe biden"
    addr = 0x00000001
    while addr != 0:
        addr_bytes = stream.read(4)
        if len(addr_bytes) < 4:
            break
        addr = int.from_bytes(addr_bytes, "little")
        func = stream.read(40).decode(errors="ignore").strip().strip("\0")
        if addr != 0:
            result.append({"func":func,"addr":addr})
    return result

def unwrap(txt: str, size):
    txtlines = txt.splitlines()
    result = ""
    for line in txtlines:
        if len(line) == size:
            result += line
        else:
            result += line + "\r\n"
    return result

if len(sys.argv) < 3:
    showhelp()
    exit()

s = serial.Serial(sys.argv[1])
s.timeout = 3

if sys.argv[2] == "help":
    showhelp()
    exit()

if sys.argv[2] == "getcrash":
    print("getting bluescreen details...")
    bsod = dumpmem(0x91F3B8B8, 0x91F3D400, s)
    if bsod == None:
        print("FAIL AT: dumpmem(0x91F3B8B8, 0x91F3D400, s)")
        exit()
    if not bsod.decode().startswith("S/W version:"):
        print("WRONG MEMORY ADDRESS!!! (make a dump of (0x90000000, 0xA0000000)\r\nand manually search for the text...)")
        exit()
    print(unwrap(bsod.decode().strip("\x5F\x0F"), 25))
    print('-'*35)
    print("simplified dump")
    print('-'*35)
    pc_lr_addrs = dumpmem(0x91F3B840, 0x91F3B8B7, s)
    if pc_lr_addrs == None:
        print("FAIL AT: dumpmem(0x91F3B840, 0x91F3B8B7, s)")
        exit()
    stream = io.BytesIO(pc_lr_addrs)
    mochaStackCount = int.from_bytes(stream.read(4), "little")
    pc = int.from_bytes(stream.read(4), "little")
    lr = int.from_bytes(stream.read(4), "little")
    pc_symbol = stream.read(37).decode().strip().strip("\0")
    lr_symbol = stream.read(37).decode().strip().strip("\0")
    runner = stream.read(34).decode().strip().strip("\0")
    if pc_symbol == "":
        pc_symbol = "No symbol found"
    if lr_symbol == "":
        lr_symbol = "No symbol found"
    if runner == "":
        runner = "[no runner present]"
    print(f"PC: 0x{pc:08X} ({pc_symbol})")
    print(f"LR: 0x{lr:08X} ({lr_symbol})")
    print(f"Running Task: {runner}")
    print(f"Count of items in Mocha callstack: {mochaStackCount}")
    if runner != "[no runner present]":
        print("\r\nRunning Task Callstack (detailed):")
        stack = dumpmem(0x91F3ADE8, 0x91F3B30F, s)
        if stack == None:
            print(f"FAIL AT: dumpmem(0x91F3ADE8, 0x91F3B30F, s)")
            exit()
        for sack in parseCallstack(stack):
            print(f"0x{sack["addr"]:08X}, {sack["func"]}")
    print("\r\nMocha Task Callstack (detailed):")
    stack = dumpmem(0x91F3B310, 0x91F3B840, s)
    if stack == None:
        print(f"FAIL AT: dumpmem(0x91F3B310, 0x91F3B840, s)")
        exit()
    for sack in parseCallstack(stack):
        print(f"0x{sack["addr"]:08X}, {sack["func"]}")
    exit()

if sys.argv[2] == "nandsize":
    print("getting NAND size...")
    nandsz = dumpmem(0x01EEEFFC, 0x01EEEFFF, s)
    if nandsz == None:
        print(f"FAIL AT: dumpmem(0x01EEEFFC, 0x01EEEFFF, s)")
        exit()
    nandsz_readable = sizehelper(int.from_bytes(nandsz, 'little'))
    print(f"NAND size: {nandsz_readable[0]} {nandsz_readable[1]}")
    exit()

if sys.argv[2] == "getinfo":
    print("getting pointer to build info...")
    pointy = dumpmem(0x01FFFFFC, 0x01FFFFFF, s)
    if pointy == None:
        print(f"FAIL AT: dumpmem(0x01FFFFFC, 0x01FFFFFF, s)")
        exit()
    buildinfoPtr = int.from_bytes(pointy[0:4], 'little')
    the = int.from_bytes(pointy[4:8], 'little')
    something = int.from_bytes(pointy[8:12], 'little')
    print(f"buildinfoPtr = {buildinfoPtr:08X}")
    print(f"the          = {the:08X}")
    print(f"something    = {something:08X}")
    if (the != 0x12345678):
        print("FAIL AT: if (the != 0x12345678)")
        exit()
    print("getting build info...")
    buildinfo = dumpmem(buildinfoPtr, buildinfoPtr+0x100, s)
    if buildinfo == None:
        print(f"FAIL AT: dumpmem(0x{buildinfoPtr:08X}, 0x{buildinfoPtr+0x100:08X}, s)")
        exit()
    print()
    print(buildinfo.split(b'\x1a')[0].decode().strip().strip("\0"))
    exit()

if sys.argv[2] == "sendraw":
    for i in range(3, len(sys.argv)):
        print(f"sending {sys.argv[i]} to {sys.argv[1]}")
        s.write(sys.argv[i].encode().ljust(12, b'\x00'))
        time.sleep(1)
        print(s.read_all().hex())
    exit()

if sys.argv[2] == "halt":
    print(f"halting {sys.argv[1]}!")
    # enter while true loop in bootloader
    s.write("PoWeRdOwN".encode().ljust(12, b'\x00'))
    s.close()
    exit()

if sys.argv[2] == "reboot":
    if sendcmd("PrEaMbLe", s) == False:
        print("FAIL AT: preamble")
        exit()
    if sendcmd("03FFFFFC", s) == False:
        print("FAIL AT: start addr")
        exit()
    if sendcmd("03FFFFFF", s) == False:
        print("FAIL AT: end addr")
        exit()
    print(f"rebooting device on {sys.argv[1]}!")
    s.write("DaTaXfEr".encode().ljust(12, b'\x00'))
    s.close()
    exit()

if len(sys.argv) < 5:
    #print(f"usage: {sys.argv[0]} <COM port number or device file> (sendraw <command>)|halt|reboot|(<xxxxxxxx> <yyyyyyyy> <filename>)")
    showhelp()
    exit()

if not is_valid_8char_hex(sys.argv[2]) or not is_valid_8char_hex(sys.argv[3]):
    print("wrong format!!!")
    print("start or end addr not hex or not padded!!!")
    #print(f"usage: {sys.argv[0]} <COM port number or device file> (sendraw <command>)|halt|reboot|(<xxxxxxxx> <yyyyyyyy> <filename>)")
    showhelp()
    exit()

start = int(sys.argv[2], 16)
end = int(sys.argv[3], 16) + 1
data = b""
curr_chk = 1
print(f"opened {s.name}")
for curr_start in range(start, end , 0x040000):
    curr_end = min(curr_start + 0x040000, end)
    chunk = dumpmem(curr_start, curr_end, s)
    if len(chunk) == 0:
        print("dataxfer returned NULL!!!")
        print("padding with 0x00's")
        data += b'\0'*(curr_end - curr_start)
    elif len(chunk) < (curr_end - curr_start):
        print("dataxfer returned too little data!!!")
        print("padding with 0x00's")
        data += chunk + (b'\0' * (curr_end - curr_start) - len(chunk))
    else:
        data += chunk
        print(f"dumped chunk {curr_chk}")
    curr_chk += 1
if sys.argv[4] == "-":
    print(data.hex())
    exit()
file = open(sys.argv[4], 'wb')
file.write(data)
file.close()
print(f"saved dump to {sys.argv[4]}")
