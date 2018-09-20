#include <stdlib.h>
#include <stdio.h>

int x = 100;
int main()
{
  // data stored on stack
  int   a=2;
  float b=2.5;
  static int y;

  // allocate memory on heap
  int *ptr = (int *) malloc(2*sizeof(int));
  
  // values 5 and 6 stored on heap
  ptr[0]=5;
  ptr[1]=6;

  // deallocate memory on heap	
  free(ptr);
 
  return 1;
}