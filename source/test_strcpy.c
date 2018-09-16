#include <string.h>
#include <stdio.h>
void main(){
  char src[40] = "Hello World \0 Extra string";
  char dest[40];
  strcpy(dest, src);
  printf("%s",dest);
}