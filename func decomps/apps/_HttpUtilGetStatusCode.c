int _HttpUtilGetStatusCode(char *rawResponseString)
{
  int StatusCode;
  undefined1 charStatusCode [16];
  undefined1 HttpVersion [16];
  
  if (rawResponseString == (char *)0x0)
  {
    StatusCode = -1;
  }
  else
  {
    AcMemsetEx(HttpVersion,0,0x10,0x10,DAT_81412cf4,0x250);
    AcMemsetEx(charStatusCode,0,0x10,0x10,DAT_81412cf4,DAT_81412e18);
    __0sscanf(rawResponseString,s_%s_%s_81412e1c,HttpVersion,charStatusCode);
    StatusCode = AcAtoi(charStatusCode);
    SysDebugPrintf(DAT_81412d70,s__HttpUtilGetStatusCode:_Version:_81412e24,HttpVersion,StatusCode);
  }
  return StatusCode;
}


