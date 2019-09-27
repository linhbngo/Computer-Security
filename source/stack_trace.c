#include<stdio.h>
static void display(int i, int *ptr);
    
int main(void) {
 int x = 5;
 int *xptr = 5;
 printf("In main():\n");
 printf("   x is %d and is stored at %p.\n", x, &x);
 printf("   xptr points to %p which holds %d.\n", xptr, *xptr);
 display(x, xptr);
 printf ("The display function has stopped\n");
 return 0;
}
   
void display(int z, int *zptr) {
  printf("In display():\n");
  printf("   z is %d and is stored at %p.\n", z, &z);
  printf("   zptr points to %p which holds %d.\n", zptr, *zptr);
}
