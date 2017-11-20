%{
#include <stdio.h>
#include <stdlib.h>
#include "commandHandler.h"
%}

%union {
    char text[128];
    int integer;
    float floating;
}
%token SET
%token PRINT
%token HELP
%token EXIT
%token <text> INSTR
%token <text> CAMOBJ
%token <text> PARAM
%token <integer> INT
%token <floating> FLOAT
%token NL

%%
line:           NL {return 0;}
                | setCommand NL {return 0;} 
                | printCommand NL {return 0;} 
                | helpCommand NL  {return 0;} 
                | exitCommand NL  {return 0;}

setCommand:     SET INSTR PARAM INT         {handleSetInstrPI($2, $3, $4);}
                | SET INSTR PARAM FLOAT FLOAT   {handleSetInstrPFF($2, $3, $4, $5);}
                | SET INSTR PARAM FLOAT     {handleSetInstrPF($2, $3, $4);}
                | SET PARAM FLOAT           {handleSetPF($2, $3);}

printCommand:   PRINT PARAM          {handlePrintP($2);}
                | PRINT INSTR        {handlePrintInstr($2);}
                | PRINT INSTR PARAM  {handlePrintInstrP($2, $3);}
                | PRINT CAMOBJ       {handlePrintCamobj($2);}
                | PRINT CAMOBJ PARAM {handlePrintCamobjP($2, $3);}

helpCommand:    HELP {handleHelp();}

exitCommand:    EXIT {handleExit();}
                
