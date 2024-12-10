import math
import argparse


def roughly_equal(in1, in2, tolerance):
    return abs(in1 - in2) < tolerance


def maidenhead_precision_div(precision):
    if precision == 0:
        return 18
    elif precision % 2 == 1:
        return 10
    else:
        return 24


def maidenhead_precision_char(precision):
    if precision == 0:
        return 'A'
    elif precision % 2 == 1:
        return '0'
    else:
        return 'a'


def maidenheadgriddiv(thing, maxthingval, maxprecision):
    out = ""
    for i in range(maxprecision):
        div = maidenhead_precision_div(i)
        c = maidenhead_precision_char(i)
        maxthingval /= div
        t = int(thing / maxthingval)
        thing -= t * maxthingval
        out += chr(t + ord(c))
    return out


def maidenhead_to_latlon(loc):
    lat = 0
    lon = 0
    loclen = len(loc)
    latdiv = 1
    londiv = 1
    for i in range(loclen):
        precision = i // 2
        div = maidenhead_precision_div(precision)
        c = maidenhead_precision_char(precision)
        charval = ord(loc[i]) - ord(c)
        if i % 2 == 0:
            londiv *= div
            lon += (charval / londiv) * 360
        else:
            latdiv *= div
            lat += (charval / latdiv) * 180
    lon -= 180
    lat -= 90
    return lat, lon


def latlon_to_maidenhead(lat, lon, precision):
    lon += 180
    lat += 90
    maidenhead_out = ''.join(''.join(pair) for pair in zip(maidenheadgriddiv(lon, 360, precision), maidenheadgriddiv(lat, 180, precision)))
    return maidenhead_out


def distance_between_maidenheads_in_subsquares(a, b):
    scale = [240, 24, 1]
    lonsubsquarediff = 0
    latsubsquarediff = 0
    for i in range(6):
        chardiff = ord(b[i]) - ord(a[i])
        subsquare_diff = chardiff * scale[i // 2]
        if i % 2 == 0:
            lonsubsquarediff += subsquare_diff
        else:
            latsubsquarediff += subsquare_diff
    if lonsubsquarediff >= 2160:
        lonsubsquarediff -= 4320
    return math.sqrt(latsubsquarediff**2 + lonsubsquarediff**2)


def maidenheads_are_adjacent(a, b):
    return distance_between_maidenheads_in_subsquares(a, b) < 2
class GridSquare:
    def __init__(self, maidenhead):
        self.maidenhead = maidenhead
        self.lat, self.lon = maidenhead_to_latlon(maidenhead)

    def __eq__(self, other):
        if isinstance(other, GridSquare):
            return self.maidenhead == other.maidenhead
        elif isinstance(other, str):
            return self.maidenhead == other
        elif isinstance(other, tuple) and len(other) == 2:
            lat, lon = other
            return latlon_within_maidenhead(lat, lon, self.maidenhead)
        return False
    @classmethod
    def from_latlon(cls, lat, lon, precision=3):
        maidenhead = latlon_to_maidenhead(lat, lon, precision)
        return cls(maidenhead)

    def distance_to(self, other):
        if isinstance(other, GridSquare):
            lat1, lon1 = math.radians(self.lat), math.radians(self.lon)
            lat2, lon2 = math.radians(other.lat), math.radians(other.lon)
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return 6371.0 * c  # Earth radius in kilometers
        raise ValueError("Distance can only be calculated between GridSquare instances")


def latlon_within_maidenhead(lat, lon, loc):
    c1_lat, c1_lon = maidenhead_to_latlon(loc)
    loc_list = list(loc)
    loc_list[-1] = chr(ord(loc_list[-1]) + 1)
    loc_list[-2] = chr(ord(loc_list[-2]) + 1)
    c2_lat, c2_lon = maidenhead_to_latlon(''.join(loc_list))
    return c1_lat <= lat < c2_lat and c1_lon <= lon < c2_lon


def main():
    parser = argparse.ArgumentParser(description="Maidenhead Grid Square Converter")
    parser.add_argument('-g', '--grid', type=str, help='Convert Maidenhead to Lat/Lon')
    parser.add_argument('-l', '--latlon', type=str, help='Convert Lat/Lon to Maidenhead, format: lat,lon')
    parser.add_argument('-p', '--precision', type=int, default=3, help='Precision for Maidenhead conversion')
    args = parser.parse_args()

    if args.grid:
        lat, lon = maidenhead_to_latlon(args.grid)
        print(f"{lat},{lon}")

    if args.latlon:
        lat, lon = map(float, args.latlon.split(','))
        maidenhead = latlon_to_maidenhead(lat, lon, args.precision)
        print(maidenhead)

if __name__ == "__main__":
    main()
