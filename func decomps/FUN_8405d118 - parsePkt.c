void parsePkt(char *packet)
{
  byte bVar1;
  ushort uVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  
  iVar3 = 841E6D40;
  uVar8 = 0;
  do
  {
    while( true )
    {
      uVar7 = *(uint *)(841E6D40 + 0x58);
      if ((uVar7 <= uVar8) || (*(int *)(841E6D40 + 0x50) == 1))
      {
        return;
      }
      bVar1 = packet[uVar8];
      uVar4 = (uint)bVar1;
      if (uVar4 != 0xffffffff) break;
      *(undefined4 *)(iVar3 + 0x1c) = 0;
    }
    iVar6 = *(int *)(iVar3 + 0x1c);
    if (iVar6 == 0)
    {
      if (uVar4 == 0x7e)
      {
        uVar5 = 1;
LAB_8405d180:
        *(undefined4 *)(iVar3 + 0x1c) = uVar5;
      }
      goto LAB_8405d1f0;
    }
    if (iVar6 == 1)
    {
      if (uVar4 == 0x7e) goto LAB_8405d1f0;
      *(undefined2 *)(iVar3 + 4) = 0;
      *(undefined2 *)(iVar3 + 6) = 0xffff;
      *(undefined4 *)(iVar3 + 0x1c) = 2;
      uVar8 += 1;
      *(byte *)(841E6D40 + 0x54) = bVar1;
      uVar4 = (uint)(byte)packet[uVar8];
LAB_8405d160:
      if (uVar4 == 0x7e)
      {
        if (*(ushort *)(iVar3 + 4) < 3)
        {
          uVar5 = 4;
        }
        else
        {
          if (*(ushort *)(iVar3 + 6) == 0000F0B8)
          {
            uVar5 = 3;
            goto LAB_8405d180;
          }
          uVar5 = 1;
        }
        FUN_8405f770(uVar5);
        goto LAB_8405d19a;
      }
      if (uVar4 == 0x7d)
      {
        uVar8 += 1;
        if (uVar8 == uVar7)
        {
          *(undefined4 *)(iVar3 + 0x18) = 1;
          goto LAB_8405d1f0;
        }
        if ((byte)packet[uVar8] == 0xffffffff) goto LAB_8405d19a;
        uVar4 = (byte)packet[uVar8] ^ 0x20;
      }
      if (*(int *)(iVar3 + 0x18) == 1)
      {
        *(undefined4 *)(iVar3 + 0x18) = 0;
        if (uVar4 == 0xffffffff) goto LAB_8405d19a;
        uVar2 = *(ushort *)(iVar3 + 4);
        *(char *)(*(int *)(84069800 + 8) + (uint)uVar2) = (char)(uVar4 ^ 0x20);
        *(ushort *)(iVar3 + 4) = uVar2 + 1;
        *(ushort *)(iVar3 + 6) =
             *(ushort *)(iVar3 + 6) >> 8 ^
             *(ushort *)
              (84060FE8 + ((((uint)*(ushort *)(iVar3 + 6) ^ uVar4 ^ 0x20) << 0x18) >> 0x17));
      }
      else
      {
        uVar2 = *(ushort *)(iVar3 + 4);
        *(char *)(*(int *)(84069800 + 8) + (uint)uVar2) = (char)uVar4;
        *(ushort *)(iVar3 + 4) = uVar2 + 1;
        *(ushort *)(iVar3 + 6) =
             *(ushort *)(iVar3 + 6) >> 8 ^
             *(ushort *)(84060FE8 + (((*(ushort *)(iVar3 + 6) ^ uVar4) << 0x18) >> 0x17));
      }
    }
    else
    {
      if (iVar6 == 2) goto LAB_8405d160;
LAB_8405d19a:
      *(undefined4 *)(iVar3 + 0x1c) = 0;
    }
LAB_8405d1f0:
    iVar6 = 841E6D40;
    uVar8 += 1;
    if (*(int *)(iVar3 + 0x1c) == 3)
    {
      *(undefined4 *)(iVar3 + 0x1c) = 0;
      uVar8 = 0;
      *(undefined4 *)(iVar6 + 0x50) = 1;
    }
  } while( true );
}
