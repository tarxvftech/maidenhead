/*#define MAIDENHEAD_TESTING*/
//enables main() and test functions
/*#define LOUD*/
//only useful when MAIDENHEAD_TESTING, is a little more verbose

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include "maidenhead.h"
#include "math.h"
#include "string.h"


#define SHOULD_MATCH 1
#define DONT_MATCH   0

//TODO: write a function to generate adjacent gridsquares by mangling an existing one
int roughly_equal(double in1, double in2, double tolerance){
    return fabs(in1 - in2) < tolerance;
}

int maidenhead_precision_div(int precision){
    int div;
    if(precision==0){//first (field) is divisions of 18 with a capital letter
        div=18;
    }else if(precision%2==1){//squares and every odd precision level are divisions of 10 
        div=10;
    } else { //and every even level that isn't 0 is divisions of 24
        div=24;
    }
    return div;
}
int maidenhead_precision_char(int precision){
    char c;
    if(precision==0){//first (field) is divisions of 18 with a capital letter
        c='A';
    }else if(precision%2==1){//squares and every odd precision level are divisions of 10 
        c='0';
    } else { //and every even level that isn't 0 is divisions of 24
        c='a';//could be capital, but it's become more common to see letters lowercase after the first set, e.g. FN41sp
    }
    return c;
}
void maidenheadgriddiv(double thing, double maxthingval, int maxprecision, char * out ){
    //expects "out" to be 2*maxprecision in size
    //determines whether this thing is lat or lon based on "maxthingval"
    //supports extended arbitrary precision by continuing the 10, 24 pattern
    int ifwearelat = maxthingval==180;
    for(int i =0; i < maxprecision; i++ ){
        int offset;
        int t;
        int div = maidenhead_precision_div(i);
        char c = maidenhead_precision_char(i);
        maxthingval /= div;
        t = thing/maxthingval;
        thing -= t*maxthingval;
        offset = ifwearelat? i*2+1: i*2;
        out[offset] = t + c;
    }
    return;
}




latlon maidenhead_to_latlon( char * loc ){
    latlon out;

    out.lat = 0;
    out.lon = 0;
    int loclen = strlen(loc);
    /*int max_precision = loclen/2;*/

    int latdiv = 1;
    int londiv = 1;
    for( int i = 0; i < loclen; i++){
        int precision = i/2;
        int div = maidenhead_precision_div(precision);
        char c = maidenhead_precision_char(precision);
        int charval = loc[i] - c;
        if( i%2 == 0){
            londiv *= div;
            out.lon += ((double)charval / (double)londiv) * 360;
        } else {
            latdiv *= div;
            out.lat += ((double)charval / (double)latdiv) * 180;
        }

    }
    out.lon -= 180;
    out.lat -= 90;

    return out;
}
void maidenhead_to_lat_lon( char * loc, double * lat, double * lon ){
    latlon xy = maidenhead_to_latlon( loc );
    *lat = xy.lat;
    *lon = xy.lon;
}


void latlon_to_maidenhead( latlon in, char * maidenhead_out, int precision ){
    double lon = in.lon + 180;
    double lat = in.lat + 90;
    maidenheadgriddiv(lon, 360, precision ,maidenhead_out);
    maidenheadgriddiv(lat, 180, precision ,maidenhead_out);
}
void lat_lon_to_maidenhead( double lat, double lon, char * maidenhead_out, int precision ){
    latlon xy;
    xy.lat = lat;
    xy.lon = lon;
    latlon_to_maidenhead( xy, maidenhead_out, precision);
}




double distance_between_maidenheads_in_km(char*a,char*b){
    return 0;
}
double m_sqrt(double in){
    //https://stackoverflow.com/a/29019938
    double root =in/3;
    int i;
    if (in <= 0) return 0;
    for (i=0; i<32; i++)
        root = (root + in / root) / 2;
    return root;
}
double distance_between_maidenheads_in_subsquares(char*a,char*b){
    //only supports down to subsquares
    /*
    -------------------------------------------
    |             |             |             |
    |   FN42ab    |   FN42bb    |   FN42cb    |
    |             |             |             |
    |-------------|-------------|-------------|
    |             |             |             |
    |   FN42aa    |   FN42ba    |   FN42ca    |
    |             |             |             |
    -------------------------------------------
    */
    //find x distance
    //find y distance
    //return sqrt( x**2 + y**2 )
    //
    // assume six character maidenhead max
    /*
    The first pair (a field) encodes with base 18 and the letters "A" to "R".
        18 zones of longitude of 20° each, and 18 zones of latitude 10° each
    The second pair (square) encodes with base 10 and the digits "0" to "9".
        1° of latitude by 2° of longitude
    The third pair (subsquare) encodes with base 24 and the letters "a" to "x".
        2.5' of latitude by 5' of longitude
    The fourth pair (extended square) encodes with base 10 and the digits "0" to "9". (we don't use this (yet?))
    */
    int scale[]={240,24,1};
    int lonsubsquarediff=0;
    int latsubsquarediff=0;
    for( int i =0; i < 6; i++){ //6 because 6 characters, 3 levels
        int chardiff = b[i] - a[i]; //so a->c should be positive 'motion'
        int subsquare_diff = chardiff * scale[i/2]; 
        if( i % 2 == 0 ){ // a[0,2,4] are the lon
            lonsubsquarediff += subsquare_diff;
        } else {// a[1,3,5] are the lat
            latsubsquarediff += subsquare_diff;
        }
    }
    if( lonsubsquarediff >= 2160 ){
        lonsubsquarediff -= 4320; //double check this in morning
    }
    return m_sqrt( (double)latsubsquarediff*latsubsquarediff + (double)lonsubsquarediff*lonsubsquarediff);

}
int maidenheads_are_adjacent( char *a, char *b){
    return distance_between_maidenheads_in_subsquares(a,b) < 2; 
    //includes diagonals: if we dont want diagonals change to == 1
}






/* code above, tests below */




#ifdef MAIDENHEAD_TESTING
int test_maidenhead_distances(char * a,char * b,double expected_subsquare_distance){
    int errors = 0;
    double d = distance_between_maidenheads_in_subsquares(a,b);
    if( ! roughly_equal(d,expected_subsquare_distance, 1e-9) ){
        printf("\nError in gridsubsquare distance calculation for %s and %s\n\tGot %f but expected %f\n",a,b,d,expected_subsquare_distance);
        errors += 1;
    }
    if( expected_subsquare_distance < 2 && ! maidenheads_are_adjacent(a,b) ){
        printf("Error in gridsubsquare adjacency calculation\n\tGot false but expected true\n");
        errors += 1;
    }
    if( expected_subsquare_distance >= 2 && maidenheads_are_adjacent(a,b) ){
        printf("Error in gridsubsquare adjacency calculation\n\tGot true but expected false\n");
        errors += 1;
    }
#ifdef LOUD
    printf("%s to %s: %f subsquares expected %f\n\tadjacent: %s\n",a,b,d,expected_subsquare_distance,maidenheads_are_adjacent(a,b)?"true":"false");
#endif
    return errors;
}
int test_latlon_to_maidenhead(latlon in, char * expected_maidenhead, int expect_match ){
    int errors = 0;
    int len = strlen(expected_maidenhead);
    char * out = malloc( len+1 );
    memset(out, 0, len+1); 
    int levels = strlen(expected_maidenhead)/2;
    latlon_to_maidenhead( in, out, levels );
    if( strlen(out) != 2*levels ){
        printf("Incorrect precision for latlon to maidenhead where expected_maidenhead == %s\n"
                "\tGot %s\n",expected_maidenhead,out);
        errors++;
    }
    if( (strncmp(out,expected_maidenhead, levels*2) == 0) != expect_match){
        printf("Bad maidenhead out for latlon to maidenhead where expected_maidenhead %s %s\n",expect_match?"==":"!=", expected_maidenhead);
        errors++;
    }
#ifdef LOUD
    printf("latlon to maidenhead: %f, %f -> %s, expected %s\n",in.lat,in.lon,out,expected_maidenhead);
#endif
    free(out);
    return errors;
}

int between(double needle, double hay, double stack){
    int result = (hay <= needle && needle <= stack ) ||
        (stack <= needle && needle <= hay);
    return result;
}
int latlon_between( latlon needle, latlon hay, latlon stack ){
    return between( needle.lat, hay.lat, stack.lat ) && 
            between( needle.lon, hay.lon, stack.lon );
}
int latlon_within_maidenhead(latlon in, char * loc){
    latlon c1 = {0,0}; //corner1
    latlon c2 = {0,0}; //corner2

    int len = strlen(loc);
    char * mh = malloc( len+1 );
    memset(mh, 0, len+1); 


    //generate lat and lon pairs for each of the adjacent squares
    //(the lat/lon of which are actually a specific corner)
    //
    //you don't actually have to generate all of them of course, just
    //the far corner
    memcpy(mh, loc, len);
    mh[len-1]++;
    mh[len-2]++;
    c1 = maidenhead_to_latlon(loc);
    c2 = maidenhead_to_latlon(mh);
#ifdef LOUD
    printf("c1 %f, %f %s\n", c1.lat, c1.lon, loc);
    printf("in %f, %f \n",   in.lat, in.lon);
    printf("c2 %f, %f %s\n", c2.lat, c2.lon, mh);
#endif
    //then check out incoming latlon against those latlons
    int result = latlon_between( in, c1, c2);
#ifdef LOUD
    printf("%s\n\n", result?"yes":"no");
#endif

    
    return result;
}
int maidenhead_within_maidenhead_square(){
    return 0;
}
int test_maidenhead_to_latlon(char * in, latlon expected, int expect_match ){
    int errors = 0;
    latlon out = maidenhead_to_latlon(in);
    if( latlon_within_maidenhead(expected, in) != expect_match ){
        printf("maidenhead to latlon: %s -> %f,%f, target %f,%f %s expected within bounds\n",in, out.lat, out.lon, expected.lat, expected.lon, expect_match?"":"not" );
        errors++;
    }
    return errors;
}
void test(){
    int errors = 0;
    errors += test_maidenhead_distances( "FN42aa", "FN42ab", 1);
    errors += test_maidenhead_distances( "FN42aa", "FN42ba", 1);
    errors += test_maidenhead_distances( "FN42aa", "FN42bb", sqrt(2));
    errors += test_maidenhead_distances( "FN42ca", "FN42aa", 2);
    errors += test_maidenhead_distances( "FN43aa", "FN42aa", 24);
    errors += test_maidenhead_distances( "FN42aa", "FN42aa", 0);

    //longitude wrap-around, double check me!
    errors += test_maidenhead_distances( "AA00aa", "IA00aa", 1920); 
    errors += test_maidenhead_distances( "AA00aa", "IA90xa", 2159); 
    errors += test_maidenhead_distances( "AA00aa", "JA00aa", 2160); //dead opposite long, if I'm right
    errors += test_maidenhead_distances( "AA00aa", "JA00ba", 2159); 
    errors += test_maidenhead_distances( "AA00aa", "KA00aa", 1920); 
    errors += test_maidenhead_distances( "AA00aa", "RA90xa", 1); 
    errors += test_maidenhead_distances( "AA00aa", "RA90wa", 2); 

    errors += test_maidenhead_distances( "AA00aa", "AR09ax", 4319); 
        //max diff in latitude, but double check in morning
    
    latlon in;
    in.lat = 0;
    in.lon = 0;
    errors += test_latlon_to_maidenhead(in,"JJ00", SHOULD_MATCH);
    errors += test_latlon_to_maidenhead(in,"JJ00aa", SHOULD_MATCH);
    in.lon = -71.32457;
    in.lat = 42.65148;
    errors += test_latlon_to_maidenhead(in,"FN42", SHOULD_MATCH);
    errors += test_latlon_to_maidenhead(in,"FN42ip", SHOULD_MATCH);
    errors += test_latlon_to_maidenhead(in,"FN42ip16", SHOULD_MATCH);
    errors += test_latlon_to_maidenhead(in,"FN42ip16bi", SHOULD_MATCH);

    errors += test_maidenhead_to_latlon("JJ00",in, DONT_MATCH);
    errors += test_maidenhead_to_latlon("FN",in, SHOULD_MATCH);
    errors += test_maidenhead_to_latlon("FN42",in, SHOULD_MATCH);
    errors += test_maidenhead_to_latlon("FN42ip",in, SHOULD_MATCH);
    errors += test_maidenhead_to_latlon("FN42ip16",in, SHOULD_MATCH);
    errors += test_maidenhead_to_latlon("FN42ip16bi",in, SHOULD_MATCH);
    errors += test_maidenhead_to_latlon("FN42ip16bi25js47",in, DONT_MATCH); //beyond double representation
        
    printf("\nCompleted tests with %d errors.\n",errors);
}

int main(int argc, char **argv){
    //Use standard arg parsing, please fill out main (and any includes)
    //for executing the following functions on demand from the CLI:
    //test();
    //void maidenhead_to_lat_lon( char * loc, double * lat, double * lon );
    //void lat_lon_to_maidenhead( double lat, double lon, char * maidenhead_out, int precision );
    int opt;
    char *loc = NULL;
    double lat = 0.0, lon = 0.0;
    char maidenhead_out[64] = {0};
    int precision = 3; //has to be specified first
    while ((opt = getopt(argc, argv, "p:Tg:l:")) != -1) {
        switch (opt) {
            case 'T':
                test();
                break;
            case 'p':
                sscanf(optarg, "%d",&precision);
                break;
            case 'g':
                loc = optarg;
                maidenhead_to_lat_lon(loc, &lat, &lon);
                printf("%lf,%lf\n",lat,lon);
                break;
            case 'l':
                // For this example, assume input is "lat,lon"
                if (sscanf(optarg, "%lf,%lf", &lat, &lon) != 2) {
                    fprintf(stderr, "Invalid format for -l. Expected format: lat,lon\n");
                    return 1;
                }
                lat_lon_to_maidenhead(lat, lon, maidenhead_out, precision);
                printf("%s\n",maidenhead_out);
                break;
            default:
                fprintf(stderr, "Usage: %s [-T] [-g loc] [-l lat,lon]\n", argv[0]);
                return 1;
        }
    }

    return 0;
}
/*
(gcc -DLOUD -DMAIDENHEAD_TESTING maidenhead.c -o maidenhead -lm;./maidenhead)
*/
#endif
