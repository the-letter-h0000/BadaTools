bool PhlSvcLockVerifyPhoneLockPasswd(char *szPasswd)
{
  char storedPass[512]; // 1 NVRAM block
  if (szPasswd == (char *)0x0)
  {
    _SysAssertReport(1,"ASSERTION_REQUIRE","szPasswd != NULL","PhlSvcPhoneLock.c",0x41);
  }
  else
  {
    NvGetString(0x17c,storedPass);
    if (AcStrcmp(storedPass,szPasswd) == 0)
    {
      return true;
    }
  }
  return false;
}
