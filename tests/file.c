/*
  file.c -- simple file handling tools
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

/* supported commands
 *
 * delete name - deletes "name"
 * new name [content] - creates "name" and writes "content" to it (if defined)
 */

int main(int argc, char *argv[]) {
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "delete") == 0) {
            if (++i == argc) {
                fprintf(stderr, "not enough arguments for delete\n");
                return 1;
            }
            if (remove(argv[i]) != 0) {
                fprintf(stderr, "error deleting '%s': %s\n", argv[i], strerror(errno));
                return 1;
            }
        }
        else if (strcmp(argv[i], "new") == 0) {
            FILE *out;
            if (++i == argc) {
                fprintf(stderr, "not enough arguments for new\n");
                return 1;
            }
            if ((out = fopen(argv[i], "w")) == NULL) {
                fprintf(stderr, "error creating '%s': %s\n", argv[i], strerror(errno));
                return 1;
            }
            if (++i < argc) {
                if (fprintf(out, "%s\n", argv[i]) < 0) {
                    fprintf(stderr, "error writing to '%s': %s\n", argv[i], strerror(errno));
                    return 1;
                }
            }
            if (fclose(out) < 0) {
                fprintf(stderr, "error closing '%s': %s\n", argv[i], strerror(errno));
                return 1;
            }
        }
    }
    return 0;
}
