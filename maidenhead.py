import unittest

class latlon():
    def __init__(self, lat : float, lon : float):
        self.lat = lat
        self.lon = lon

def roughly_equal(in1 : float, in2 : float, tolerance : float) -> int:
    return int(abs(in1-in2)< tolerance)

def maidenhead_precision_div(precision : int) -> int:
    div = 0
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
    c = 'c'
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

def maidenhead_grid_div(thing : float, maxthingval : float, maxprecision : int, out : str):
    # expects "out" to be 2*maxprecision in size
    # determines whether this thing is lat or lon based on "maxthingval"
    # supports extended arbitrary precision by continuing the 10, 24 pattern
    ifwearelat = maxthingval == 180
    for i in range(0, maxprecision):
        offset, t = 0, 0
        div, c = maidenhead_precision_div(i), maidenhead_precision_char(i)
        maxthingval /= div
        t = thing/maxthingval
        thing -= t*maxthingval
        offset = (i*2)+1 if ifwearelat else i*2
        out[offset] = t+c

def maidenhad_to_latlon(loc : str) -> latlon:
    out = latlon(0.0,0.0)

    loclen = len(loc)

    latdiv = 1
    londiv = 1
    for i in range(0, loclen):
        precision = i/2
        div, c = maidenhead_precision_div(precision), maidenhead_precision_char(precision)
        charval = loc[i] - c
        if(i%2 == 0):
            londiv *= div
            out.lon += (float(charval)/float(londiv)) * 360
        else:
            latdiv *= div
            out.lat += (float(charval)/float(latdiv)) * 180

    out.lon -= 180
    out.lat -= 90

    return out

def maidenhead_to_latlon(x : latlon, maidenhead_out : str, precision: int):
    lon = x.lon + 180
    lat = x.lat + 90
    maidenhead_grid_div(lon, 360, precision, maidenhead_out)
    maidenhead_grid_div(lat, 180, precision, maidenhead_out)

def lat_lon_to_maidenhead(lat : float, lon : float, maidenhead_out : str, precision : int):
    xy = latlon( lat, lon )
    lat_lon_to_maidenhead(xy, maidenhead_out, precision)


def distance_between_maidenheads_in_km(a : str, b : str):
    return 0

def m_sqrt(x : float) -> float:
    # https://stackoverflow.com/a/29019938
    root = x/3
    i = 0
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
        chardiff = b[i] - a[i] # so a->c should be positive 'motion'
        subsquare_diff = chardiff * scale[i/2]
        if(i%2 == 0):
            # a[0,2,4] are the lon
            lonsubsquarediff += subsquare_diff
        else:
            # a[1,3,5] are the lat
            latsubsquarediff += subsquare_diff

    if(lonsubsquarediff >= 2160):
        lonsubsquarediff -= 4320

    return m_sqrt(float(latsubsquarediff^2)+float(lonsubsquarediff^2))

def maidenheads_are_adjacent(a : str, b : str) -> int:
    return int(distance_between_maidenheads_in_subsquares(a, b)<2)

'''
Code above, tests below
'''

class TestMaidenhead(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def test_maidenhead_distances():
        return 0

    def test_latlon_to_maidenhead():
        return 0

    def test_maidenhead_to_latlon():
        return 0

    def test():
        return 0