# BadaTools
tools for BadaOS 1.1 devices

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

## Decompilation tools
### readFunclist.py
Dumps the function list in uncompressed_apps.bin (from 0x04340008 to 0x04E29953) in a readable format, must take the function list out of uncompressed_apps.bin yourself (using a hex editor)

Requirements:
- Python 3
