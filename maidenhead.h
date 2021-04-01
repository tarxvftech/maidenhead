#ifndef _MAIDENHEAD_H
#define _MAIDENHEAD_H


typedef struct latlon {
	float lat;
	float lon;
} latlon;


// parse a nul terminated string like "FN41sp" to the appropriate lat-lon.
latlon maidenhead_locator_to_latlon( char * loc );

// encode a lat-lon into a maidenhead grid square
// precision is how many levels to encode, e.g. FN41 is 2, FN41sp is 3, etc
void latlon_to_maidenhead_locator( latlon in, char * maidenhead_out, int precision );

//
float distance_between_maidenhead_locators_in_subsquares(char*a,char*b);
int maidenhead_locators_are_adjacent( char *a, char *b);

#endif
