%{
    #include "y.tab.h"
    #include <stdio.h>
%}

set     (set)
print   (print)
help    (help)
exit    (exit)
instr   (instr)[1-2]
camObj  (camobj)[1-2]
param   [a-zA-Z]+
int     [0-9]+
float   [0-9]+.[0-9]+
nl      \n
none    .
%%

{set}       {return SET;}
{print}     {return PRINT;}
{help}      {return HELP;}
{exit}      {return EXIT;}
{instr}     {
             sscanf(yytext, "%s", yylval.text);
             return INSTR;
            }

{camObj}    {
             sscanf(yytext, "%s", yylval.text);
             return CAMOBJ;
            }

{param}     {
             sscanf(yytext, "%s", yylval.text);
             return PARAM;
            }

{int}       {
             sscanf(yytext, "%d", yylval.integer);
             return INT;
            }
{float}     {
             sscanf(yytext, "%f", yylval.floating);
             return FLOAT;
            }
{nl}        {return NL;}

%%

