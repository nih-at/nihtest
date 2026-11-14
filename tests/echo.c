/*
  echo.c -- repeat back command line
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

#include <stdio.h>
#include <string.h>

#define HEX_BUF_SIZE 8192

int hex_value(char c) {
    if (c >= '0' && c <= '9')
        return c - '0';
    if (c >= 'a' && c <= 'f')
        return c - 'a' + 10;
    if (c >= 'A' && c <= 'F')
        return c - 'A' + 10;
    return 0;
}

char* hex_decode(char* str) {
    static char buf[HEX_BUF_SIZE];
    char* out = buf;
    while (*str && out - buf < HEX_BUF_SIZE - 1) {
        if (str[0] == '\\' && str[1] == 'x' && str[2] && str[3]) {
            int val = hex_value(str[2]) * 16 + hex_value(str[3]);
            *out++ = (char)val;
            str += 4;
        }
        else {
            *out++ = *str++;
        }
    }
    *out = '\0';
    return buf;
}

int main(int argc, char* argv[]) {
    FILE* out = stdout;
    int start = 1;
    int hex = 0;
    while (1) {
        if (start < argc && strcmp(argv[start], "-e") == 0) {
            start++;
            out = stderr;
        }
        else if (start < argc && strcmp(argv[start], "-x") == 0) {
            start++;
            // handle -x option here if needed
            hex = 1;
        }
        else {
            break;
        }
    }
    for (int i = start; i < argc; i++) {
        fprintf(out, "%s%s", (i == start ? "" : " "), hex ? hex_decode(argv[i]) : argv[i]);
    }
    fprintf(out, "\n");
    return 0;
}
