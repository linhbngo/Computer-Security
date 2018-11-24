#include <stdio.h>

int main()
{
  int   id = 100, age = 25;
  char *name = "Bob Smith";
  char *statement = "ID: %d, Name: %s, Age: %d\n"; 
  printf (statement, id, name);

  return 1;
}