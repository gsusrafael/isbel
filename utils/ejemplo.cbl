       IDENTIFICATION DIVISION.
       PROGRAM-ID. HELLO-WORLD.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 datos PIC X(90).

       PROCEDURE DIVISION.
       ACCEPT datos 
    	  FROM COMMAND-LINE
       END-ACCEPT.
  
       DISPLAY 
    	  datos
       END-DISPLAY.
  
       STOP RUN.
