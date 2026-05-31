void parseCmdVal(void)
{
  int iVar1;
  byte *pbVar2;
  undefined4 uVar3;
  byte command;
  
  iVar1 = DAT_8405d2e0;
  pbVar2 = *(byte **)(DAT_8405d2e0 + 4);
  command = *pbVar2;
  if (command == 0xa0)
  {
LAB_8405d24c:
    uVar3 = 0;
  }
  else
  {
    if (command < 0xa1)
    {
      if (command == 0x60)
      {
        FUN_8404afe8();
        return;
      }
      if (command < 0x61)
      {
        if (((command == 0x23) || (command == 0x24)) || (command == 0x25))
        {
          return;
        }
        if (command == 0x50) goto LAB_8405d24c;
      }
      else
      {
                    // get info (dump memory from bootloader
                    // from 0x84069810 to 0x840698F3)
        if (command == 0x70)
        {
          getInfo();
          return;
        }
        if (command == 0x71)
        {
          FUN_8404b220();
          return;
        }
        if (command == 0x80)
        {
          FUN_8404b1fc();
          return;
        }
                    // restart device
        if (command == 0x90)
        {
          FUN_84004460(*DAT_8405d2e4);
          FUN_8404b17c(*(undefined4 *)(iVar1 + 4));
          return;
        }
      }
    }
    else
    {
      if (command == 0xdd)
      {
        FUN_8404b234();
        return;
      }
      if (command < 0xde)
      {
        if (command == 0xb2)
        {
          FUN_8404af30();
          return;
        }
        if (command == 0xb3)
        {
          FUN_8401bd00();
          pbVar2 = *(byte **)(iVar1 + 4);
LAB_8405d2b6:
          FUN_8404af8c(pbVar2);
          return;
        }
        if (command == 0xb4) goto LAB_8405d2b6;
        if (command == 0xc0)
        {
          FUN_8404b10c();
          return;
        }
      }
      else
      {
        if ((command == 0xee) || (command == 0xef))
        {
          FUN_8404b000();
          return;
        }
        if (command == 0xf0)
        {
          FUN_8404b08c();
          return;
        }
      }
    }
    uVar3 = 6;
  }
  FUN_8405f770(uVar3);
  return;
}
