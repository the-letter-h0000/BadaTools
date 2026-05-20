// WARNING: Globals starting with '_' overlap smaller symbols at the same address

undefined4 __RbmCHSendLCDDisplayData(uint screenIndex,uint chunkIndex)
{
  int iVar1;
  int iVar2;
  undefined1 *puVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  char *pcVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  undefined8 uVar11;
  undefined4 local_44;
  int LcdHeight;
  int LcdWidth;
  int local_38;
  uint local_34;
  uint local_30;
  undefined4 local_2c;
  int local_28;
  uint local_24;
  uint totalPixels;
  uint uStack_1c;
  uint local_18;
  
  iVar9 = 0;
  local_44 = 0x10;
  local_28 = 0;
  local_2c = 0;
  uStack_1c = screenIndex;
  local_18 = chunkIndex;
  LcdWidth = SysGetLcdWidth(screenIndex);
  LcdHeight = SysGetLcdHeight(screenIndex);
  totalPixels = LcdHeight * LcdWidth;
  if (totalPixels < DAT_83162a9c)
  {
    local_34 = 0x800;
  }
  else
  {
    local_34 = 0x1000;
  }
  local_38 = local_34 * 2 + 0xf;
  local_30 = local_34;
  iVar1 = LcdScreenBufferAlloc(screenIndex);
  iVar2 = DAT_83162aa0;
  *(int *)(DAT_83162aa0 + 0x24) = iVar1;
  if (iVar1 == 0)
  {
                    // WARNING: Subroutine does not return
    SysDebugPrintf(0xba,DAT_831629c4 + 0xd8);
  }
  if (local_18 == 0)
  {
    *(undefined4 *)(iVar2 + 0x20) = 0;
    iVar1 = LcdGetScreenMergedBuffer((int)(char)screenIndex,iVar1);
    *(int *)(iVar2 + 0x20) = iVar1;
  }
  else
  {
    iVar1 = *(int *)(iVar2 + 0x20);
  }
  if (iVar1 == 0)
  {
                    // WARNING: Subroutine does not return
    SysDebugPrintf(0xba,_DAT_83162ad8,screenIndex,*(undefined4 *)(iVar2 + 0x24));
  }
  iVar2 = *(int *)(iVar2 + 0x24);
  if ((screenIndex == 0) || (screenIndex == 1))
  {
    local_24 = __aeabi_uidivmod(totalPixels,local_30);
    if (local_18 <= local_24)
    {
      iVar1 = _BmIsPowerOffState();
      if (iVar1 == 1)
      {
                    // WARNING: Subroutine does not return
        SysDebugPrintf(0xba,DAT_83162f20);
      }
      puVar3 = (undefined1 *)MemAllocTraceEx(0,local_38 + -3,DAT_83162f24,DAT_83162f28);
      if (puVar3 == (undefined1 *)0x0)
      {
        iVar9 = DAT_83162f20 + 0x48;
      }
      else
      {
        iVar1 = MemAllocTraceEx(0,local_38 << 1,DAT_83162f24,DAT_83162f28 + 7);
        if (iVar1 != 0)
        {
          if (local_24 == local_18)
          {
            AcMemsetEx(puVar3,0,local_38 + -3,4,DAT_83162f24,DAT_83162f28 + 0x10);
            local_34 = totalPixels - local_30 * local_18;
          }
          *puVar3 = 0x22;
          iVar4 = DAT_83162f28;
          uVar6 = DAT_83162f24;
          puVar3[1] = (char)screenIndex;
          AcMemcpyEx(puVar3 + 2,&local_18,2,4,uVar6,iVar4 + 0x1a);
          iVar4 = DAT_83162f28;
          puVar3[4] = 0;
          AcMemcpyEx(puVar3 + 5,&local_44,2,4,DAT_83162f24,iVar4 + 0x20);
          iVar8 = 0;
          iVar4 = OemPhsGetLCDType();
          if (iVar4 != 0)
          {
            uVar11 = __aeabi_uidivmod(local_30 * local_18,LcdHeight);
            iVar9 = (int)((ulonglong)uVar11 >> 0x20);
            local_28 = (int)uVar11 + 1;
          }
          for (uVar10 = 0; uVar10 < local_34; uVar10 += 1)
          {
            iVar4 = OemPhsGetLCDType();
            if (iVar4 == 0)
            {
              uVar5 = local_30 * local_18 + uVar10;
              if (totalPixels * 2 - 1 <= uVar5) break;
              puVar3[iVar8 + 7] = (char)*(undefined2 *)(iVar2 + uVar5 * 2);
              puVar3[iVar8 + 8] =
                   (char)((ushort)*(undefined2 *)(iVar2 + (local_30 * local_18 + uVar10) * 2) >> 8);
            }
            else
            {
              iVar4 = LcdWidth * ((LcdHeight - iVar9) + -1);
              if (totalPixels * 2 - 1 <= (uint)(iVar4 + local_28 + -1)) break;
              iVar4 = (iVar4 + local_28) * 2 + iVar2;
              puVar3[iVar8 + 7] = (char)*(undefined2 *)(iVar4 + -2);
              puVar3[iVar8 + 8] = (char)((ushort)*(undefined2 *)(iVar4 + -2) >> 8);
              if (iVar9 == LcdHeight + -1)
              {
                local_28 += 1;
                iVar9 = 0;
              }
              else
              {
                iVar9 += 1;
              }
            }
            iVar8 += 2;
          }
          puVar3[local_38 + -8] = 0;
          puVar3[local_38 + -7] = 0;
          puVar3[local_38 + -6] = 0;
          puVar3[local_38 + -5] = 0;
          puVar3[local_38 + -4] = 0;
          uVar6 = EncodePPPFrame(puVar3,local_38 - 3U & 0xffff,iVar1);
          UsbWrite(8,iVar1,uVar6);
          if (puVar3 != (undefined1 *)0x0)
          {
            MemFreeTraceMultiHeap(puVar3,DAT_83162f24,DAT_83162f28 + 0x53);
          }
          if (iVar1 != 0)
          {
            MemFreeTraceMultiHeap(iVar1,DAT_83162f24,DAT_83162f28 + 0x56);
          }
          if (local_24 == local_18)
          {
            LcdScreenBufferFree();
          }
          return 1;
        }
        iVar9 = DAT_83162f20 + 0xa4;
      }
                    // WARNING: Subroutine does not return
      SysDebugPrintf(0xba,iVar9);
    }
    pcVar7 = s_~__RbmCHSendLCDDisplayData_:_Inv_83162adb + 1;
    screenIndex = local_18;
  }
  else
  {
    pcVar7 = s___RbmCHSendLCDDisplayData_:_Inva_83162aa4;
  }
                    // WARNING: Subroutine does not return
  SysDebugPrintf(0xba,pcVar7,screenIndex);
}
