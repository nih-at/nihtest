/*
  cat.c -- simple file/stdin output
  Copyright (C) 2020 Dieter Baron and Thomas Klausner

  This file is part of nihtest, regression tests for command line utilities.
  The authors can be contacted at <nihtest@nih.at>

  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions
  are met:
  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the
     distribution.
  3. The names of the authors may not be used to endorse or promote
     products derived from this software without specific prior
     written permission.

  THIS SOFTWARE IS PROVIDED BY THE AUTHORS ``AS IS'' AND ANY EXPRESS
  OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
  ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY
  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
  GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
  IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
  IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#ifdef _MSC_VER
// We're okay with using the incredibly insecure functions fopen() and sterror().
// (Yes, it's not thread save, and we're not multi-threaded.)
#define _CRT_SECURE_NO_WARNINGS
#endif

#include <errno.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
    int i = 1;

    FILE *out = stdout;

    if (strcmp(argv[i], "-e") == 0) {
        out = stderr;
        i++;
    }

    for (; i<argc; i++) {
        FILE *in;
        size_t ret;
        char buf[1024];
        if (strcmp(argv[i], "-") == 0) {
            in = stdin;
        } else {
            in = fopen(argv[i], "r");
        }
        if (in == NULL) {
            fprintf(stderr, "cannot open '%s': %s", argv[i], strerror(errno));
            continue;
        }
        while ((ret = fread(buf, 1, sizeof(buf), in)) > 0) {
            fwrite(buf, 1, ret, stdout);
        }
        if (in != stdin) {
            fclose(in);
        }
    }
    return 0;
}
