#include <stdlib.h>
#include <stdio.h>

int x = 100;
int main()
{
  // data stored on stack
  int   a=2;
  double b=2.5;
  int   c=4;
  static int y;

  // allocate memory on heap
  int *ptr = (int *) malloc(2*sizeof(int));
  
  // values 5 and 6 stored on heap
  ptr[0]=5;
  ptr[1]=6;


  printf ("x is %d and is stored at %p\n", x, &x);
  printf ("a is %d and is stored at %p\n", a, &a);
  printf ("b is %f and is stored at %p\n", b, &b);
  printf ("c is %d and is stored at %p\n", c, &c);
  printf ("y is %d and is stored at %p\n", y, &y);
  printf ("ptr[0] is %d and is stored at %p\n", ptr[0], &ptr[0]);
  printf ("ptr[1] is %d and is stored at %p\n", ptr[1], &ptr[1]);

  // deallocate memory on heap	
  free(ptr);
  return 1;
}