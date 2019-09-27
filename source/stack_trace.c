#include<stdio.h>
static void display(int i, int *ptr);
    
int main(void) {
 int x;
 int *xptr;
 printf("In main():\n");
 x = 5;
 xptr = &x;
 printf("   x is %d and is stored at %p.\n", x, &x);
 printf("   xptr points to %p which holds %d.\n", xptr, *xptr);
 display(x, xptr);
 printf ("The display function has stopped\n");
 return 0;
}
   
void display(int z, int *zptr) {
  int y;
  printf("In display():\n");
  y = 10;
  printf("   z is %d and is stored at %p.\n", z, &z);
  printf("   zptr points to %p which holds %d.\n", zptr, *zptr);
  *zptr = 16; 
}
