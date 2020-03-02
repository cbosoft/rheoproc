#include <stdlib.h>
#include <stdio.h>
#include <stdarg.h>
#include <errno.h>
#include <string.h>
#include <time.h>

#include "err.h"

#define MESGLEN 100

void ferr(int showerrno, const char *source, const char* fmt, ...)
{
  char mesg[MESGLEN] = {0};

  va_list ap;

  va_start(ap, fmt);
  vsnprintf(mesg, MESGLEN-1, fmt, ap);
  va_end(ap);

  time_t rt;
  struct tm *info;
  char timestr[MESGLEN] = {0};

  time(&rt);
  info = localtime(&rt);
  strftime(timestr, MESGLEN-1, "%x %X", info);

  fprintf(stderr, "  (%s) FATAL ERROR! in %s: %s", timestr, source, mesg);
  if (showerrno)
    fprintf(stderr, " (%d) %s", errno, strerror(errno));
  fprintf(stderr, "\n");

  exit(1);
}
