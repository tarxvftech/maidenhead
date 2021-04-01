maidenhead: maidenhead.c
	#gcc -DLOUD -DMAIDENHEAD_TESTING $^ -o $@ -lm
	gcc -DMAIDENHEAD_TESTING $^ -o $@ -lm
	./$@
clean:
	-rm maidenhead
