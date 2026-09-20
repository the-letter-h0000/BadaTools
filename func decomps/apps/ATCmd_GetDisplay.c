undefined4 ATCmd_GetDisplay(undefined4 param_1,void *HANDLE,int commandMode,char *displayNum,char *chunkNum)
{
  undefined1 iDisplayNum;
  undefined2 iChunkNum;
  int iVar1;
  // Accepts display 1 (when other Wave devices have only a single display)
  // leftover from SCH-W689 (Duos W689)
  // results in a hard crash on other devices when calling LcdScreenBufferFree
  if ((((commandMode == 3) || (commandMode == 1)) || (commandMode == 2)) &&
     ((iVar1 = strcmp("0",displayNum), iVar1 == 0 || (iVar1 = strcmp("1",displayNum), iVar1 == 0))))
  {
    iDisplayNum = strtol(displayNum,0,10);
    iChunkNum = strtol(chunkNum,0,10);
    iVar1 = __RbmCHSendLCDDisplayData(iDisplayNum,iChunkNum);
    if (iVar1 != 0)
    {
      AT_CmdRspOK(HANDLE);
      return 1;
    }
  }
  AT_CmdRspError(HANDLE,602); // return +CME ERROR: 602
  return 0xffffffff;
}

