int _HttpUtilGetStatusCode(char *HttpStatusLine)
{
  int statusCode;
  char szHttpStatusCode[16];
  char szHttpVersion[16];
  
  if (HttpStatusLine == (char *)0x0)
  {
    statusCode = -1;
  }
  else
  {
    AcMemsetEx(szHttpVersion,0,0x10,0x10,DAT_81412cf4,0x250);
    AcMemsetEx(szHttpStatusCode,0,0x10,0x10,DAT_81412cf4,DAT_81412e18);
    __0sscanf(HttpStatusLine,"%s %s ",szHttpVersion,szHttpStatusCode);
    statusCode = AcAtoi(szHttpStatusCode);
    SysDebugPrintf(DAT_81412d70,"_HttpUtilGetStatusCode: Version: %s Status: %d\n",szHttpVersion,statusCode);
  }
  return statusCode;
}
