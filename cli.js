#!/usr/bin/env node

const GridSquare = require('./maidenhead.js');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

const argv = yargs(hideBin(process.argv))
    .option('grid', {
        alias: 'g',
        type: 'string',
        description: 'Convert Maidenhead to Lat/Lon'
    })
    .option('latlon', {
        alias: 'l',
        type: 'string',
        description: 'Convert Lat/Lon to Maidenhead, format: lat,lon'
    })
    .option('precision', {
        alias: 'p',
        type: 'number',
        default: 3,
        description: 'Precision for Maidenhead conversion'
    })
    .help()
    .argv;

if (argv.grid) {
    const [lat, lon] = GridSquare.maidenheadToLatLon(argv.grid);
    console.log(`${lat},${lon}`);
}

if (argv.latlon) {
    const [lat, lon] = argv.latlon.split(',').map(Number);
    const maidenhead = GridSquare.latLonToMaidenhead(lat, lon, argv.precision);
    console.log(`${maidenhead}`);
}

