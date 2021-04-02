#ifndef _MAIDENHEAD_H
#define _MAIDENHEAD_H


typedef struct latlon {
	float lat;
	float lon;
} latlon;


// parse a nul terminated string like "FN41sp" to the appropriate lat-lon.
latlon maidenhead_to_latlon( char * loc );
void maidenhead_to_lat_lon( char * loc, float * lat, float * lon );

// encode a lat-lon into a maidenhead grid square
// precision is how many levels to encode, e.g. FN41 is 2, FN41sp is 3, etc
// you're expected to provide a buffer that can fit the grid square, the needed size is 
// precision*2 (and +1 for the nul terminator if you're doing that)
//
// TODO?: latlon_to_maidenhead_locator doesn't set that nul!
// initialize the buffer to 0, or keep track of the string length yourself to avoid issues
void latlon_to_maidenhead( latlon in, char * maidenhead_out, int precision );
void lat_lon_to_maidenhead( float lat, float lon, char * maidenhead_out, int precision );

//
float distance_between_maidenhead_locators_in_subsquares(char*a,char*b);
int maidenhead_locators_are_adjacent( char *a, char *b);

#endif
