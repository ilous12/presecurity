#include <stdio.h>
#include <string.h>

void copy_name(const char *input) {
  char name[16];
  // Intentional fixture: unbounded copy into a fixed-size buffer.
  strcpy(name, input);
  printf("%s\n", name);
}
