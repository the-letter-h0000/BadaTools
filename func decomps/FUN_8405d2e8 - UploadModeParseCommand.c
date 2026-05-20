void UploadModeParseCommand(char *command)
{
  undefined4 uVar1;
  int iVar2;
  size_t sVar3;
  uint startAddr;
  char *pcVar4;
  uint uVar5;
  int iVar6;
  undefined4 uVar7;
  int iVar8;
  uint uVar9;
  int local_58;
  char dataxfer_chunk1 [4];
  char dataxfer_chunk2 [4];
  char dataxfer_chunk3 [4];
  char powerdown_chunk1 [4];
  char powerdown_chunk2 [4];
  char powerdown_chunk3 [4];
  char postamble_chunk1 [4];
  char postamble_chunk2 [4];
  char postamble_chunk3 [4];
  char acknowledgment_chunk1 [4];
  char acknowledgment_chunk2 [4];
  char acknowledgment_chunk3 [4];
  char acknowledgment_chunk4 [4];
  char preamble_chunk1 [4];
  char preamble_chunk2 [4];
  char preamble_chunk3 [4];
  astruct_1 *UMSession;
  
  preamble_chunk1 = (char  [4])s_PrEaMbLe_8405d4b8._0_4_;
  preamble_chunk2 = (char  [4])s_PrEaMbLe_8405d4b8._4_4_;
  preamble_chunk3 = (char  [4])s_PrEaMbLe_8405d4b8._8_4_;
  acknowledgment_chunk1 = (char  [4])s_AcKnOwLeDgMeNt_8405d4c4._0_4_;
  acknowledgment_chunk2 = (char  [4])s_AcKnOwLeDgMeNt_8405d4c4._4_4_;
  acknowledgment_chunk3 = (char  [4])s_AcKnOwLeDgMeNt_8405d4c4._8_4_;
  acknowledgment_chunk4 = (char  [4])s_AcKnOwLeDgMeNt_8405d4c4._12_4_;
  postamble_chunk1 = (char  [4])s_PoStAmBlE_8405d4d4._0_4_;
  postamble_chunk2 = (char  [4])s_PoStAmBlE_8405d4d4._4_4_;
  postamble_chunk3 = (char  [4])s_PoStAmBlE_8405d4d4._8_4_;
  powerdown_chunk1 = (char  [4])s_PoWeRdOwN_8405d4e0._0_4_;
  powerdown_chunk2 = (char  [4])s_PoWeRdOwN_8405d4e0._4_4_;
  powerdown_chunk3 = (char  [4])s_PoWeRdOwN_8405d4e0._8_4_;
  dataxfer_chunk1 = (char  [4])s_DaTaXfEr_8405d4ec._0_4_;
  dataxfer_chunk2 = (char  [4])s_DaTaXfEr_8405d4ec._4_4_;
  dataxfer_chunk3 = (char  [4])s_DaTaXfEr_8405d4ec._8_4_;
  iVar2 = strcmp(command,powerdown_chunk1);
  if (iVar2 == 0)
  {
    do
    {
                    // WARNING: Do nothing block with infinite loop
                    // stop comms and do not respond
    } while( true );
  }
  iVar2 = strcmp(command,preamble_chunk1);
  UMSession = 841E6D40;
  if (iVar2 == 0)
  {
    iVar2 = 1;
  }
  else
  {
    if (((841E6D40->mode != 1) && (841E6D40->mode != 2)) || (sVar3 = strlen(command), sVar3 != 8))
    {
      if ((UMSession->mode != 3) ||
         ((iVar2 = strcmp(command,dataxfer_chunk1), iVar2 != 0 &&
          (iVar2 = strcmp(command,acknowledgment_chunk1), iVar2 != 0))))
      {
        UMSession->mode = 0;
        return;
      }
      iVar2 = 841F6DC0;
      startAddr = UMSession->startAddr;
                    // return [BuildInfoPtr] 0x12345678 0xyyyyyyyy
      if ((startAddr == 01FFFFFC) && (UMSession->endAddr == startAddr + 3))
      {
        uVar7 = 0xc;
        *(undefined4 *)(841F6DC0 + 0x40) = *8FF00004;
        uVar1 = 12345678;
        *(undefined4 *)(iVar2 + 0x48) = 0xb0000000;
        *(undefined4 *)(iVar2 + 0x44) = uVar1;
      }
      else
      {
        if ((startAddr == 03FFFFFC) && (UMSession->endAddr == startAddr + 3))
        {
          rebootDevice();
          return;
        }
        if ((startAddr != 01EEEFFC) || (UMSession->endAddr != startAddr + 3))
        {
          if (startAddr <= UMSession->endAddr)
          {
            iVar8 = UMSession->endAddr - startAddr;
            iVar2 = 0x40000;
            if (iVar8 + 1U < 0x40001)
            {
              iVar2 = iVar8 + 1;
            }
            local_58 = iVar2;
            if ((startAddr < 0xb0000000) || (UMSession->field64_0x4c + 0xb0000000U <= startAddr))
            {
              if (startAddr + 0x60000000 < 12500000)
              {
                if (startAddr == 12500000 * 0x200)
                {
                  FUN_840179ac(&841E6D40->field8_0x8);
                  UMSession->field8_0x8 = 0;
                }
                FUN_8405d848(841F6DC0 + 0x40,UMSession->startAddr + 0x50000000,iVar2,&local_58);
              }
              else
              {
                if (startAddr < 0xf0000000) goto LAB_8405d49a;
                FUN_8405d550(841F6DC0 + 0x40,startAddr & 0xfffffff,iVar2);
              }
            }
            else
            {
              FUN_8405d774(841F6DC0 + 0x40,startAddr + 0x50000000,iVar2,&local_58);
            }
            startAddr = 841F6DC0 + 0x40;
LAB_8405d49a:
            writeOut(startAddr,local_58);
            UMSession->startAddr = UMSession->startAddr + local_58;
            return;
          }
          uVar7 = 10;
          pcVar4 = postamble_chunk1;
          UMSession->mode = 0;
          goto LAB_8405d4ae;
        }
                    // return size of the flash dump (FSR_BML_GetDumpSize)
        FUN_84017c5c(0);
        FUN_8405de98(&841E6D40->field64_0x4c);
        uVar7 = 4;
        *(int *)(iVar2 + 0x40) = UMSession->field64_0x4c;
      }
      pcVar4 = (char *)(841F6DC0 + 0x40);
      goto LAB_8405d4ae;
    }
    iVar8 = 1;
    startAddr = 0;
    iVar2 = 8;
    do
    {
      uVar5 = (uint)(byte)command[iVar2 + -1];
      uVar9 = uVar5 - 0x30;
      if (9 < uVar9)
      {
        if (uVar5 - 0x61 < 0x1a)
        {
          uVar9 = uVar5 - 0x57;
        }
        else
        {
          uVar9 = uVar5 - 0x37;
        }
      }
      iVar6 = iVar8 * uVar9;
      iVar8 <<= 4;
      startAddr = iVar6 + startAddr;
      iVar2 += -1;
    } while (iVar2 != 0);
    if (UMSession->mode == 1)
    {
      iVar2 = 2;
      UMSession->startAddr = startAddr;
    }
    else
    {
      iVar2 = 3;
      UMSession->endAddr = startAddr;
    }
  }
  UMSession->mode = iVar2;
  uVar7 = 0xf;
  pcVar4 = acknowledgment_chunk1;
LAB_8405d4ae:
  writeOut(pcVar4,uVar7);
  return;
}
