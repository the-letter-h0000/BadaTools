undefined4 ATCmd_GetDisplay(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4,undefined4 param_5)
{
  undefined4 uVar1;
  undefined1 uVar2;
  undefined2 uVar3;
  int iVar4;
  
  uVar1 = DAT_8192c334;
  if ((((param_3 == 3) || (param_3 == 1)) || (param_3 == 2)) &&
     ((iVar4 = strcmp(&DAT_8192c338,param_4), iVar4 == 0 ||
      (iVar4 = strcmp(&DAT_8192c33c,param_4), iVar4 == 0))))
  {
    uVar2 = strtol(param_4,0,10);
    uVar3 = strtol(param_5,0,10);
    iVar4 = __RbmCHSendLCDDisplayData(uVar2,uVar3);
    if (iVar4 != 0)
    {
      AT_CmdRspOK(param_2);
      return 1;
    }
  }
  AT_CmdRspError(param_2,uVar1);
  return 0xffffffff;
}
