#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char** argv) {

  char buf[8];

  if (read(0, buf, 8) < 1) {
    printf("Hum?\n");
    exit(1);
  }

  if (buf[0] == '0'){    
    for (int i=0;i <=50;i++){
      if (buf[0] ==  buf[1] ){
        printf("same\n");
      }      
    }
    if (buf[1] =='1'){
      printf ("second is 1\n");
    }
    printf("Bad!\n");
      
  }
  else{
    for (int i=0;i <=10;i++){     
      if (buf[0] ==  buf[1] ){
        printf("same\n");
      }
    }
    if (buf[1] =='1'){
      printf ("second is 1\n");
    }
    printf("Good!\n");
  }

  exit(0);

}
