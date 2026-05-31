# BadaTools
tools for SHP / BadaOS 1.1 devices (BadaOS 2.0 not tested because i don't have a BOS2.0 device)

source of firmware used for decomp:

https://archive.org/details/gt-s7230e - contains uncompressed binaries (uncompress_apps.bin, etc) decompressed using RevSkills, also serves as a backup if MF link goes down

https://www.mediafire.com/file/7m44zywxz3sy1k4/GT-S7230E.rar/file

# Tools included
## General tools
### SamsungWaveScreenshot.py
Direct framebuffer dumper using AT commands, outputs uncompressed pixel perfect screenshots to a PNG (Bada has a built-in screenshot key combo but it uses lossy JPGs instead...)

Requirements:
- Python 3
- pyserial
- Pillow

### SHPUploadModeDumper.py
Dumps RAM from Samsung phones running SHP in Upload Mode (as a result of an assert or exception while Debug Level is higher than Low), includes some extra functions such as dumping the bluescreen details, getting NAND size, getting build info, and restarting the device

Requirements:
- Python 3
- pyserial

### dload.py
sends user input as Download Mode commands to the device in Download Mode

Requirements:
- Python 3
- pyserial

### TkShell.py
sends TkShell commands to the device, available commands are in `documentation/Wave723_TkShellCmds.txt`

## Decompilation tools
### readFunclist.py
Dumps the function list in uncompressed_apps.bin (0x04340000) to a readable format, also converts addresses lower than 0x81000000 to image base offsets for use in Ghidra

Examples:
```
start: 0x7C047D3C (0x81DC7D3C), end: 0x7C047D40 (0x81DC7D40) - AmLedBlink
start: 0x813E162A, end: 0x813E1696 - SimGetIccidInfo
```

Requirements:
- Python 3
