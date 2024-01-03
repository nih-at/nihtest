/*
uppercase.c -- 

Copyright (C) Dieter Baron

The authors can be contacted at <assembler@tpau.group>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. The names of the authors may not be used to endorse or promote
  products derived from this software without specific prior
  written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHORS "AS IS" AND ANY EXPRESS
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

#include <ctype.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "usage: %s: input output\n", argv[0]);
    }

    FILE *in = fopen(argv[1], "r");
    if (in == NULL) {
        fprintf(stderr, "%s: can't open '%s': %s\n", argv[0], argv[1], strerror(errno));
        exit(1);
    }

    FILE *out = fopen(argv[2], "w");
    if (out == NULL) {
        fprintf(stderr, "%s: can't create '%s': %s\n", argv[0], argv[2], strerror(errno));
        exit(1);
    }

    unsigned char buf[512];
    size_t n;

    while (((n=fread(buf, 1, sizeof(buf), in))) > 0) {
        for (size_t i=0; i < n; i++) {
            if (islower(buf[i])) {
                buf[i] = toupper(buf[i]);
            }
        }
        if (fwrite(buf, 1, n, out) != n) {
            fprintf(stderr, "%s: can't write to '%s': %s\n", argv[0], argv[2], strerror(errno));
            exit(1);
        }
    }

    if (ferror(in)) {
        fprintf(stderr, "%s: can't read from '%s': %s\n", argv[0], argv[1], strerror(errno));
        exit(1);
    }
    fclose(in);

    if (fclose(out) != 0) {
        fprintf(stderr, "%s: can't write to '%s': %s\n", argv[0], argv[2], strerror(errno));
        exit(1);
    }

    exit(0);
}
