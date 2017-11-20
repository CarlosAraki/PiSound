standard:
	yacc -d parser.y
	flex parser.l
	gcc -g -o main -I/usr/include/python2.7 main.c y.tab.c lex.yy.c -L./lib/ -lm -lcsound64 -lpython2.7 -lpthread -ly -lfl
	sudo cp Imagem.py /usr/lib/python2.7/

clean:
	rm lex.yy.c y.tab.c y.tab.h ./main
