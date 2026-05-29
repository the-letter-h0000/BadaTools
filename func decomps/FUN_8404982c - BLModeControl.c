void BLModeControl(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)
{
  int *piVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  int reason;
  char *pcVar4;
  
  uVar3 = DAT_84049928;
  puVar2 = DAT_84049924;
  piVar1 = DAT_84049920;
  reason = *DAT_84049920;
  if (reason == 0x10)
  {
    logUart(DAT_84049928,s_AST_DOWNLOAD_84049998,param_3,param_4,param_4);
                    // enableUSB is a guess, not sure what it does because
                    // it's spaghetti spezzati all over the damn place
    enableUSB(0);
    writeDownloadBannerToLcd();
  }
  else
  {
    if (reason < 0x11)
    {
      if ((reason == 1) || (reason == 2))
      {
        FUN_84018a6c();
        if (*piVar1 == 1)
        {
          logUart(uVar3,s_AST_POWERON_84049948);
        }
        if (*piVar1 == 2)
        {
          logUart(uVar3,s_AST_POWERON_LPM_84049958);
        }
        *puVar2 = 0;
        FUN_8404ad2c();
      }
      else
      {
        if (reason != 4)
        {
          if (reason == 8)
          {
            if (*(int *)(*DAT_8404992c + 0x3fc) == 0)
            {
              pcVar4 = s_AST_UPLOAD_84049988;
            }
            else
            {
              pcVar4 = s_AST_BLUESCREEN_84049930;
            }
            logUart(DAT_84049928,pcVar4,param_3,param_4,param_4);
            writeUploadBannerToLcd();
            initUploadModeProtocol();
            return;
          }
          goto LAB_84049918;
        }
        FUN_84018a6c();
        logUart(uVar3,s_AST_POWERON_ALARM_8404996c);
        FUN_8404aed8();
        *puVar2 = DAT_84049984;
      }
      FUN_84020618();
      return;
    }
    if (reason != 0x20)
    {
      if (reason == 0x40)
      {
        *DAT_84049924 = 0;
        FUN_8404ad18();
        return;
      }
      if (reason == 0x60)
      {
        logUart(DAT_84049928,s_DOWNLOAD_FAIL_840499a8,param_3,param_4,param_4);
        FUN_8404ac48();
        return;
      }
      if (reason == 0x80)
      {
        FUN_8404ad2c();
        FUN_8400684c(DAT_84049944);
        FUN_840072b8();
        return;
      }
LAB_84049918:
      FUN_8404aed8();
      return;
    }
    logUart(DAT_84049928,s_AST_DOWNLOAD_84049998,param_3,param_4,param_4);
    enableUSB(1);
    FUN_8404acb0();
  }
  cmsbl_dload_entry();
  return;
}
