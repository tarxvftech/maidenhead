class GridSquare {
    constructor(maidenhead) {
        this.maidenhead = maidenhead;
        [this.lat, this.lon] = GridSquare.maidenheadToLatLon(maidenhead);
    }

    static roughlyEqual(in1, in2, tolerance) {
        return Math.abs(in1 - in2) < tolerance;
    }

    static maidenheadPrecisionDiv(precision) {
        if (precision === 0) {
            return 18;
        } else if (precision % 2 === 1) {
            return 10;
        } else {
            return 24;
        }
    }

    static maidenheadPrecisionChar(precision) {
        if (precision === 0) {
            return 'A';
        } else if (precision % 2 === 1) {
            return '0';
        } else {
            return 'a';
        }
    }

    static maidenheadGridDiv(thing, maxthingval, maxprecision) {
	let out = "";
        for (let i = 0; i < maxprecision; i++) {
            const div = GridSquare.maidenheadPrecisionDiv(i);
            const c = GridSquare.maidenheadPrecisionChar(i);
            maxthingval /= div;
            let t = Math.trunc(thing / maxthingval);
            thing -= t * maxthingval;
            out += String.fromCharCode(t + c.charCodeAt(0));
        }
        return out;
    }

    static maidenheadToLatLon(loc) {
        let lat = 0;
        let lon = 0;
        const loclen = loc.length;
        let latdiv = 1;
        let londiv = 1;
        for (let i = 0; i < loclen; i++) {
            const precision = Math.floor(i / 2);
            const div = GridSquare.maidenheadPrecisionDiv(precision);
            const c = GridSquare.maidenheadPrecisionChar(precision);
            const charval = loc.charCodeAt(i) - c.charCodeAt(0);
            if (i % 2 === 0) {
                londiv *= div;
                lon += (charval / londiv) * 360;
            } else {
                latdiv *= div;
                lat += (charval / latdiv) * 180;
            }
        }
        lon -= 180;
        lat -= 90;
        return [lat, lon];
    }

    static latLonToMaidenhead(lat, lon, precision) {
        const lonPart = GridSquare.maidenheadGridDiv(lon+180, 360, precision);
        const latPart = GridSquare.maidenheadGridDiv(lat+90, 180, precision);
	let out = '';
	for( let i = 0; i < precision; i++ ){
		out += lonPart[i];
		out += latPart[i];
	}
	return out;
    }

    static distanceBetweenMaidenheadsInSubSquares(a, b) {
        const scale = [240, 24, 1];
        let lonsubsquarediff = 0;
        let latsubsquarediff = 0;
        for (let i = 0; i < 6; i++) {
            const chardiff = b.charCodeAt(i) - a.charCodeAt(i);
            const subsquareDiff = chardiff * scale[Math.floor(i / 2)];
            if (i % 2 === 0) {
                lonsubsquarediff += subsquareDiff;
            } else {
                latsubsquarediff += subsquareDiff;
            }
        }
        if (lonsubsquarediff >= 2160) {
            lonsubsquarediff -= 4320;
        }
        return Math.sqrt(latsubsquarediff ** 2 + lonsubsquarediff ** 2);
    }

    static maidenheadsAreAdjacent(a, b) {
        return GridSquare.distanceBetweenMaidenheadsInSubSquares(a, b) < 2;
    }

    static latLonWithinMaidenhead(lat, lon, loc) {
        const [c1Lat, c1Lon] = GridSquare.maidenheadToLatLon(loc);
        const locList = loc.split('');
        locList[locList.length - 1] = String.fromCharCode(locList[locList.length - 1].charCodeAt(0) + 1);
        locList[locList.length - 2] = String.fromCharCode(locList[locList.length - 2].charCodeAt(0) + 1);
        const [c2Lat, c2Lon] = GridSquare.maidenheadToLatLon(locList.join(''));
        return c1Lat <= lat && lat < c2Lat && c1Lon <= lon && lon < c2Lon;
    }

    static fromLatLon(lat, lon, precision = 3) {
        const maidenhead = GridSquare.latLonToMaidenhead(lat, lon, precision);
        return new GridSquare(maidenhead);
    }

    distanceTo(other) {
        if (other instanceof GridSquare) {
            const lat1 = this.lat * Math.PI / 180;
            const lon1 = this.lon * Math.PI / 180;
            const lat2 = other.lat * Math.PI / 180;
            const lon2 = other.lon * Math.PI / 180;
            const dlat = lat2 - lat1;
            const dlon = lon2 - lon1;
            const a = Math.sin(dlat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dlon / 2) ** 2;
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            return 6371.0 * c; // Earth radius in kilometers
        }
        throw new Error("Distance can only be calculated between GridSquare instances");
    }

    equals(other) {
        if (other instanceof GridSquare) {
            return this.maidenhead === other.maidenhead;
        } else if (typeof other === 'string') {
            return this.maidenhead === other;
        } else if (Array.isArray(other) && other.length === 2) {
            const [lat, lon] = other;
            return GridSquare.latLonWithinMaidenhead(lat, lon, this.maidenhead);
        }
        return false;
    }
}

module.exports = GridSquare;

//console.log(GridSquare.maidenheadGridDiv(-71.32457+180, 360, 3));
//console.log(GridSquare.maidenheadGridDiv(42.65148+90, 180, 3));
