uint EncodePPPFrame(int param_1,uint param_2,int param_3)
{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  byte bVar6;
  
  uVar4 = 0;
  uVar2 = 0;
  uVar5 = DAT_83162a94 + 1;
  bVar6 = 0;
  while (uVar4 < param_2)
  {
    bVar1 = *(byte *)(param_1 + uVar4);
    uVar3 = (uint)bVar1;
    uVar4 = uVar4 + 1 & 0xffff;
    uVar5 = uVar5 >> 8 ^ (uint)*(ushort *)(DAT_83162a98 + (((uVar5 ^ uVar3) << 0x18) >> 0x17));
    if ((uVar3 == 0x7e) || (uVar3 == 0x7d))
    {
      *(undefined1 *)(param_3 + uVar2) = 0x7d;
      uVar2 = uVar2 + 1 & 0xffff;
      *(byte *)(param_3 + uVar2) = bVar1 ^ 0x20;
      uVar2 = uVar2 + 1 & 0xffff;
    }
    else
    {
      *(byte *)(param_3 + uVar2) = bVar1;
      uVar2 = uVar2 + 1 & 0xffff;
    }
  }
  uVar5 = ~uVar5 & 0xffff;
  for (; bVar6 < 2; bVar6 += 1)
  {
    uVar4 = uVar5 & 0xff;
    bVar1 = (byte)uVar5;
    uVar5 >>= 8;
    if ((uVar4 == 0x7e) || (uVar4 == 0x7d))
    {
      *(undefined1 *)(param_3 + uVar2) = 0x7d;
      bVar1 ^= 0x20;
      uVar2 = uVar2 + 1 & 0xffff;
    }
    *(byte *)(param_3 + uVar2) = bVar1;
    uVar2 = uVar2 + 1 & 0xffff;
  }
  *(undefined1 *)(param_3 + uVar2) = 0x7e;
  return uVar2 + 1 & 0xffff;
}
