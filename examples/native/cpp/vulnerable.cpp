#include <cstring>
#include <iostream>

void copyToken(const char *token) {
  char buffer[32];
  // Intentional fixture: unbounded copy into a fixed-size buffer.
  std::strcpy(buffer, token);
  std::cout << buffer << std::endl;
}
