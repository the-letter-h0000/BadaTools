bool PhlSvcLockVerifyPhoneLockPasswd(char *szPasswd)
{
  char storedPass[512];
  
  if (szPasswd == (char *)0x0)
  {
    _SysAssertReport(1,s_ASSERTION_REQUIRE_821f07f8,s_szPasswd_!=_NULL_821f07e4,
                     s_PhlSvcPhoneLock.c_821f07d0,0x41);
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
