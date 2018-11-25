#include <stdio.h>
int main()
{
  int   a, b, c;
  a = b = c = 0x11223344;
  
  printf ("12345%n\n", &a);
  printf ("The value of a: 0x%x\n", a);
    
  printf ("12345%hn\n", &b);
  printf ("The value of a: 0x%x\n", b);
    
  printf ("12345%hhn\n", &c);
  printf ("The value of a: 0x%x\n", c);
  return 1;
}