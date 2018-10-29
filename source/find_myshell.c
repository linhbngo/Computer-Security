#include <stdio.h>

int main()
{
  char *shell = (char *) getenv("MYSHELL");
  printf ("Test testing \n");
  int x, y; 
  printf ("%d\n", x + y);
  if (shell) {
    printf ("Value: %s\n", shell);
    printf ("Address: %x\n", (unsigned int)shell); 
  }
  return 1;
}