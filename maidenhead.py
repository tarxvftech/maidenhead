SHOULD_MATCH = 1
DONT_MATCH = 0

class latlon():
    def __init__(self, lat : float, lon : float):
        self.lat = lat
        self.lon = lon

def roughly_equal(in1 : float, in2 : float, tolerance : float) -> int:
    return int(abs(in1-in2)< tolerance)

def maidenhead_precision_div(precision : int) -> int:
    div = 1
    # first (field) is divisions of 18 with a capital letter
    if(precision==0):
        div=18
    # squares and every odd precision level are divisions of 10 
    elif(precision%2==1):
        div=10
    # and every even level that isn't 0 is divisions of 24
    else:
        div=24

    return div

def maidenhead_precision_char(precision : int) -> int:
    # first (field) is divisions of 18 with a capital letter
    if(precision==0):
        c='A'
    # squares and every odd precision level are divisions of 10 
    elif(precision%2==1):
        c='0'
    # and every even level that isn't 0 is divisions of 24
    else:
        c='a'

    return c

def maidenhead_grid_div(thing : float, maxthingval : float, maxprecision : int, out : list):
    # expects "out" to be 2*maxprecision in size
    # determines whether this thing is lat or lon based on "maxthingval"
    # supports extended arbitrary precision by continuing the 10, 24 pattern
    ifwearelat = int(maxthingval==180)
    # out = list(out)
    for i in range(0, maxprecision):
        # offset = 0
        # t = 0
        div, c = maidenhead_precision_div(i), maidenhead_precision_char(i)
        maxthingval = maxthingval/div
        t = int(thing/maxthingval)
        thing -= t*maxthingval
        offset = i*2+1 if ifwearelat else i*2
        # Python string-array-string
        out[offset] = chr(int(t)+ord(c))

def maidenhead_to_latlon(loc : str) -> latlon:
    out = latlon(0.0,0.0)

    loclen = len(loc)

    latdiv = 1
    londiv = 1
    for i in range(0, loclen):
        precision = i//2
        div, c = maidenhead_precision_div(precision), maidenhead_precision_char(precision)
        charval = ord(loc[i]) - ord(c)
        if(i%2 == 0):
            londiv *= div
            out.lon += (float(charval)/float(londiv)) * 360
        else:
            latdiv *= div
            out.lat += (float(charval)/float(latdiv)) * 180

    out.lon -= 180
    out.lat -= 90

    return out

def maidenhead_to_lat_lon(loc : str, lat : float, lon : float):
    xy = maidenhead_to_latlon(loc)
    lat = xy.lat
    lon = xy.lon

def latlon_to_maidenhead(x : latlon, maidenhead_out : list, precision: int):
    lon_temp = x.lon + 180
    lat_temp = x.lat + 90
    maidenhead_grid_div(lon_temp, 360, precision, maidenhead_out)
    maidenhead_grid_div(lat_temp, 180, precision, maidenhead_out)

    return ''.join(maidenhead_out)

# def lat_lon_to_maidenhead(lat : float, lon : float, maidenhead_out : str, precision : int):
#     xy = latlon( lat, lon )
#     latlon_to_maidenhead(xy, maidenhead_out, precision)


def distance_between_maidenheads_in_km(a : str, b : str):
    return 0

def m_sqrt(x : float) -> float:
    # https://stackoverflow.com/a/29019938
    root = x/3
    if(x <= 0): return 0
    for i in range(0, 32):
        root = (root + x / root)/2
    
    return root

def distance_between_maidenheads_in_subsquares(a : str, b : str) -> float:
    '''
    only supports down to subsquares
    
    -------------------------------------------
    |             |             |             |
    |   FN42ab    |   FN42bb    |   FN42cb    |
    |             |             |             |
    |-------------|-------------|-------------|
    |             |             |             |
    |   FN42aa    |   FN42ba    |   FN42ca    |
    |             |             |             |
    -------------------------------------------
    
    find x distance
    find y distance
    return sqrt( x**2 + y**2 )
    
    assume six character maidenhead max
    
    The first pair (a field) encodes with base 18 and the letters "A" to "R".
        18 zones of longitude of 20° each, and 18 zones of latitude 10° each
    The second pair (square) encodes with base 10 and the digits "0" to "9".
        1° of latitude by 2° of longitude
    The third pair (subsquare) encodes with base 24 and the letters "a" to "x".
        2.5' of latitude by 5' of longitude
    The fourth pair (extended square) encodes with base 10 and the digits "0" to "9". (we don't use this (yet?))
    '''
    scale = [240, 24, 1]
    lonsubsquarediff=0
    latsubsquarediff=0

    # 6 because 6 characters, 3 levels
    for i in range(0, 6):
        chardiff = ord(b[i]) - ord(a[i]) # so a->c should be positive 'motion'
        subsquare_diff = chardiff * scale[i//2]
        if(i%2 == 0):
            # a[0,2,4] are the lon
            lonsubsquarediff += subsquare_diff
        else:
            # a[1,3,5] are the lat
            latsubsquarediff += subsquare_diff

    if(lonsubsquarediff >= 2160):
        lonsubsquarediff -= 4320

    return m_sqrt(float(latsubsquarediff**2)+float(lonsubsquarediff**2))

def maidenheads_are_adjacent(a : str, b : str) -> int:
    return int(distance_between_maidenheads_in_subsquares(a, b)<2)

'''
Code above, tests below
'''

def test_maidenhead_distances(a : str,b : str,expected_subsquare_distance : float) -> int:
    errors = 0
    d = distance_between_maidenheads_in_subsquares(a,b)
    print("debug ",d)
    if( not roughly_equal(d,expected_subsquare_distance, 1e-09) ):
        print(f"\nError in gridsubsquare distance calculation for {a} and {b}\n\tGot {d} but expected {expected_subsquare_distance}\n")
        errors += 1
    if( expected_subsquare_distance < 2 and (not maidenheads_are_adjacent(a,b)) ):
        print("Error in gridsubsquare adjacency calculation\n\tGot false but expected true\n")
        errors += 1
    if( expected_subsquare_distance >= 2 and maidenheads_are_adjacent(a,b) ):
        print("Error in gridsubsquare adjacency calculation\n\tGot true but expected false\n")
        errors += 1

    s = "true" if maidenheads_are_adjacent(a,b) else "false"
    print(f"{a} to {b}: {d} subsquares expected {expected_subsquare_distance}\n\tadjacent: {s}\n")

    return errors

def test_latlon_to_maidenhead(x : latlon, expected_maidenhead : str, expect_match : int ):
    errors = 0
    out = ['0']*len(expected_maidenhead)
    levels = len(expected_maidenhead)//2
    out = latlon_to_maidenhead( x, out, levels )
    if( len(out) != 2*levels ):
        print(f"Incorrect precision for latlon to maidenhead where expected_maidenhead == {expected_maidenhead}\n"
                "\tGot {out}\n",expected_maidenhead,out)
        errors+=1
    if(int(out[0:int(levels*2)] == expected_maidenhead[0:int(levels*2)]) != expect_match):
        s = "==" if expect_match else "!="
        print(f"Bad maidenhead out for latlon to maidenhead where expected_maidenhead {s} {expected_maidenhead}\n")
        errors+=1
    print(f"latlon to maidenhead: {x.lat}, {x.lon} -> {out}, expected {expected_maidenhead}\n")

    return errors;

def between(needle : float, hay : float, stack : float) -> int:
    result = (hay<=needle and needle<=stack) or (stack<=needle and needle<=hay)
    return int(result)

def latlon_between(needle : latlon, hay : latlon, stack : latlon) -> int:
    return between(needle.lat, hay.lat, stack.lat) and between(needle.lon, hay.lon, stack.lon)

def latlon_within_maidenhead(x : latlon, loc : str):
    c1 = latlon(0.0, 0.0) # Corner 1
    c2 = latlon(0.0, 0.0) # Corner 2

    n = len(loc)
    mh = '0'*(n+1)

    # generate lat and lon pairs for each of the adjacent squares
    # (the lat/lon of which are actually a specific corner)
    #     //
    # you don't actually have to generate all of them of course, just
    # the far corner
    mh = loc+mh[n:] # porting memcpy(mh, loc, len);
    mh_list = list(mh)
    mh_list[n-1] = chr(ord(mh_list[n-1])+1)# mh[len-1]++
    mh_list[n-2] = chr(ord(mh_list[n-2])+1)# mh[len-2]++
    mh = ''.join(mh_list)

    c1 = maidenhead_to_latlon(loc)
    c2 = maidenhead_to_latlon(mh)
    print(f"c1 {c1.lat}, {c1.lon} {loc}\n");
    print(f"in {c1.lat}, {c1.lon} \n");
    print(f"c2 {c2.lat}, {c2.lon} {mh}\n");

    # then check out incoming latlon against those latlons
    result = latlon_between( x, c1, c2);

    s = "yes" if result else "no"
    print(f"{s}\n\n")
    return result

def maidenhead_within_maidenhead_square():
    return 0

def test_maidenhead_to_latlon(x : str, expected : latlon, expect_match :int ):
    errors = 0
    out = maidenhead_to_latlon(x)
    val = latlon_within_maidenhead(expected, x)
    if( val != expect_match ):
        s = "" if expect_match else "not"
        print(f"maidenhead to latlon: {x} -> {out.lat},{out.lon}, target {expected.lat},{expected.lon} {s} expected within bounds\n")
        errors+=1
    return errors

def test():
    errors = 0;
    print("test1", errors)
    errors += test_maidenhead_distances( "FN42aa", "FN42ab", 1);
    errors += test_maidenhead_distances( "FN42aa", "FN42ba", 1);
    errors += test_maidenhead_distances( "FN42aa", "FN42bb", 2**0.5);
    errors += test_maidenhead_distances( "FN42ca", "FN42aa", 2);
    errors += test_maidenhead_distances( "FN43aa", "FN42aa", 24);
    errors += test_maidenhead_distances( "FN42aa", "FN42aa", 0);

    # longitude wrap-around, double check me!
    errors += test_maidenhead_distances( "AA00aa", "IA00aa", 1920); 
    errors += test_maidenhead_distances( "AA00aa", "IA90xa", 2159); 
    errors += test_maidenhead_distances( "AA00aa", "JA00aa", 2160); # dead opposite long, if I'm right
    errors += test_maidenhead_distances( "AA00aa", "JA00ba", 2159); 
    errors += test_maidenhead_distances( "AA00aa", "KA00aa", 1920); 
    errors += test_maidenhead_distances( "AA00aa", "RA90xa", 1); 
    errors += test_maidenhead_distances( "AA00aa", "RA90wa", 2); 

    errors += test_maidenhead_distances( "AA00aa", "AR09ax", 4319); 
    # max diff in latitude, but double check in morning
    print("test2", errors)
    x = latlon(0.0, 0.0)
    errors += test_latlon_to_maidenhead(x,"JJ00", SHOULD_MATCH);
    errors += test_latlon_to_maidenhead(x,"JJ00aa", SHOULD_MATCH);
    x.lon = -71.32457;
    x.lat = 42.65148;
    errors += test_latlon_to_maidenhead(x,"FN42", SHOULD_MATCH);
    errors += test_latlon_to_maidenhead(x,"FN42ip", SHOULD_MATCH);
    errors += test_latlon_to_maidenhead(x,"FN42ip16", SHOULD_MATCH);
    errors += test_latlon_to_maidenhead(x,"FN42ip16bi", SHOULD_MATCH);

    print("test3", errors)
    errors += test_maidenhead_to_latlon("JJ00",x, DONT_MATCH);
    errors += test_maidenhead_to_latlon("FN",x, SHOULD_MATCH);
    errors += test_maidenhead_to_latlon("FN42",x, SHOULD_MATCH);
    errors += test_maidenhead_to_latlon("FN42ip",x, SHOULD_MATCH);
    errors += test_maidenhead_to_latlon("FN42ip16",x, SHOULD_MATCH);
    errors += test_maidenhead_to_latlon("FN42ip16bi",x, SHOULD_MATCH);
    errors += test_maidenhead_to_latlon("FN42ip16bi25js47",x, DONT_MATCH); # beyond double representation
    print("test4", errors)
    print(f"\nCompleted tests with {errors} errors.\n")

test()