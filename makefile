maidenhead: maidenhead.c
	#gcc -DLOUD -DMAIDENHEAD_TESTING $^ -o $@ -lm
	gcc -DMAIDENHEAD_TESTING -g $^ -o $@ -lm
	./$@

valgrind: maidenhead
	valgrind ./$^
clean:
	-rm maidenhead
