(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
// include app packages
var geoparagliding = require('./geoparagliding');
var IGCParser = require('igc-parser');
var gpxParser = require('gpxparser');

class Flight {
    constructor(name) {
        this.name = name;
        this.middle_index = 0;
        this.center_lon = 0;
        this.center_lat = 0;
        this.flight_info = {};
        this.flight_info.gliderType = 0;
        this.flight_info.pilot = 0;
        this.flight_info.date = 0;
        this.flight_info.loggerType = 0;
        
        this.flight_info.number_of_point = 0;
                
        this.flight_info.start_time = 0;
        this.flight_info.stop_time = 0;
        this.flight_info.duration = 0;

        this.flight_info.distance_total = 0;
        this.flight_info.distance_start_stop = 0;
        this.flight_info.distance_max_from_start = 0;

        this.flight_info.average_speed = 0;
        this.flight_info.max_speed = 0;

        this.flight_info.average_vertical_speed = 0;
        this.flight_info.max_vertical_speed = 0;
        this.flight_info.min_vertical_speed = 0;

        this.flight_info.high = 0;
        this.flight_info.elevation_total = 0;
        this.flight_info.elevation_max = 0;
        this.flight_info.elevation_over_start = 0;
        this.flight_info.elevation_start = 0;
        this.flight_info.elevation_stop = 0;
    }

    load_file(file_content, file_format) {
        if(file_format == ".igc") {
            this.load_igc_file(file_content);
        } else if (file_format == ".gpx") {
            this.load_gpx_file(file_content);
        } else {
            console.log("ERROR: Incompatible file format");
        }
    }

    load_igc_file(file_content) {
        let igc_obj = IGCParser.parse(file_content);
        
        // Calculate center of map coordinates
        this.middle_index = Math.floor(igc_obj.fixes.length/2);
        this.center_lon   = igc_obj.fixes[this.middle_index]['longitude'];
        this.center_lat   = igc_obj.fixes[this.middle_index]['latitude'];

        // Get flights info from file
        this.flight_info.gliderType = igc_obj.gliderType;
        this.flight_info.pilot      = igc_obj.pilot;
        this.flight_info.date       = igc_obj.date;
        this.flight_info.loggerType = igc_obj.loggerType;

        // Create paragliding_info object
        this.paragliding_info = new geoparagliding.ParaglidingPoint(igc_obj.fixes);
    }

    load_gpx_file(file_content) {
        var gpx = new gpxParser();
        gpx.parse(file_content);

        // Calculate center of map coordinates
        this.middle_index = Math.floor(gpx.tracks[0].points.length/2);
        this.center_lon   = gpx.tracks[0].points[this.middle_index]['lon'];
        this.center_lat   = gpx.tracks[0].points[this.middle_index]['lat'];

        // Get flights info from file
        let flight_date = new Date(gpx.tracks[0].points[0].time);
        this.flight_info.gliderType = "None";
        this.flight_info.pilot      = "None";
        this.flight_info.date       = flight_date.toLocaleDateString('fr-CA');
        this.flight_info.loggerType = "gpx";

        // Create paragliding_info object
        let igc_obj = [];
        for(let i in gpx.tracks[0].points) {
            igc_obj[i] = {};
            flight_date = gpx.tracks[0].points[i].time;
            igc_obj[i].time = flight_date.toLocaleTimeString();
            igc_obj[i].timestamp = flight_date.getTime();
            igc_obj[i].latitude = gpx.tracks[0].points[i].lat;
            igc_obj[i].longitude = gpx.tracks[0].points[i].lon;
            igc_obj[i].pressureAltitude = gpx.tracks[0].points[i].ele;
            igc_obj[i].gpsAltitude = igc_obj[i].pressureAltitude;
        }
        this.paragliding_info = new geoparagliding.ParaglidingPoint(igc_obj);
    }

    async process_flight_info() {
        // Process points info
        this.paragliding_info.calculate_elevation();
        this.paragliding_info.calculate_distances();
        this.paragliding_info.calculate_speeds();
        this.paragliding_info.calculate_bearing();
        this.paragliding_info.calculate_finesse();
        this.paragliding_info.calculate_duration();
        // Process flight info
        this.flight_info.number_of_point = this.paragliding_info.length();
        
        this.flight_info.start_time = this.paragliding_info.start_time();
        this.flight_info.stop_time = this.paragliding_info.stop_time();
        this.flight_info.duration = this.paragliding_info.duration();

        this.flight_info.distance_total = this.paragliding_info.distance_total();
        this.flight_info.distance_start_stop = this.paragliding_info.distance_start_stop();
        this.flight_info.distance_max_from_start = this.paragliding_info.distance_max_from_start();
        
        this.flight_info.average_speed = this.paragliding_info.average_speed();
        this.flight_info.max_speed = this.paragliding_info.max_speed();
        
        this.flight_info.average_vertical_speed = this.paragliding_info.average_vertical_speed();
        this.flight_info.max_vertical_speed = this.paragliding_info.max_vertical_speed();
        this.flight_info.min_vertical_speed = this.paragliding_info.min_vertical_speed();
                
        this.flight_info.high = this.paragliding_info.high();
        this.flight_info.elevation_total = this.paragliding_info.elevation_total();
        this.flight_info.elevation_max = this.paragliding_info.elevation_max();
        this.flight_info.elevation_over_start = this.paragliding_info.elevation_over_start();

        this.flight_info.elevation_start = this.paragliding_info[0].gpsAltitude;
        this.flight_info.elevation_stop = this.paragliding_info[this.flight_info.number_of_point-1].gpsAltitude;
    }
}

module.exports = {
    Flight
  };

},{"./geoparagliding":2,"gpxparser":6,"igc-parser":7}],2:[function(require,module,exports){
// Converts degrees to radians
function to_rad(value) {
    return value * Math.PI / 180;
}
// Converts radians to degrees
function to_degrees(value) {
  var pi = Math.PI;
  return value * (180/pi);
}

// This function takes in latitude and longitude of two location and returns the distance between them as the crow flies (in m)
function calc_crow(lat1, lon1, lat2, lon2) {
  var R = 6371000; // m
  var dLat = to_rad(lat2-lat1);
  var dLon = to_rad(lon2-lon1);
  var lat1 = to_rad(lat1);
  var lat2 = to_rad(lat2);

  var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.sin(dLon/2) * Math.sin(dLon/2) * Math.cos(lat1) * Math.cos(lat2); 
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
  var d = R * c;
  return d;
}

function ms_to_kmh(s) {
  return s*3600/1000;
}

function ms_to_s(t) {
  return t/1000;
}

function s_to_time(s) {
  let date = new Date(null);
  date.setSeconds(s);
  return date.toISOString().substring(11, 19);
}

// Main class
class ParaglidingPoint {  
    constructor(object) {
      for(let item in object) {
        this[item] = object[item];
      }
    }

    length() {
      return Object.keys(this).length;
    }

    // Points attributes methods
    calculate_distances() {
      this[0].distance = 0;
      this[0].distance_total = 0;
      for(let i=1; i<this.length(); i++) {
        this[i].distance = calc_crow(this[i-1].latitude, this[i-1].longitude, this[i].latitude, this[i].longitude);
        this[i].distance_total = this[i-1].distance_total + this[i].distance;
      }
    }

    calculate_elevation() {
      this[0].elevation = 0;
      for(let i=1; i<this.length(); i++) {
        this[i].elevation = this[i].gpsAltitude - this[i-1].gpsAltitude;
      }
    }

    calculate_speeds() {
      this[0].speed = 0;
      this[0].vertical_speed = 0;
      for(let i=1; i<this.length(); i++) {
        this[i].speed = ms_to_kmh(this[i].distance / ms_to_s(this[i].timestamp - this[i-1].timestamp));
        this[i].vertical_speed = this[i].elevation / ms_to_s(this[i].timestamp - this[i-1].timestamp);
        // Protections against timestamp equal or close
        if(! isFinite(this[i].speed)) { 
          this[i].speed = this[i-1].speed;
        }
        if(! isFinite(this[i].vertical_speed)) {
          this[i].vertical_speed = this[i-1].vertical_speed;
        }
      }
    }

    calculate_bearing() {
      this[0].bearing = 0;
      for(let i=1; i<this.length(); i++) {
        let bearing = Math.atan2( Math.sin(this[i].longitude - this[i-1].longitude) * Math.cos(this[i].latitude),
                              Math.cos(this[i-1].latitude) * Math.sin(this[i].latitude) - 
                              Math.sin(this[i-1].latitude) * Math.cos(this[i].latitude) * Math.cos(this[i].longitude - this[i-1].longitude)
                            );
        this[i].bearing = to_degrees(bearing);
      }
    }

    calculate_finesse() {
      this[0].finesse = 0;
      for(let i=1; i<this.length(); i++) {
        if(this[i].gpsAltitude == this[i-1].gpsAltitude) {
          this[i].finesse = 9;
        } else {
          this[i].finesse = this[i].distance / (this[i].gpsAltitude - this[i-1].gpsAltitude);
        }
      }
    }

    calculate_duration() {
      this[0].duration = 0;
      for(let i=1; i<this.length(); i++) {
        this[i].duration = s_to_time(ms_to_s(this[i].timestamp - this[0].timestamp));
      }
    }
  
    // Multipoints method

    // Time stats    
    start_time() {
      return this[0].time;
    }

    stop_time() {
      return this[this.length()-1].time;
    }

    duration() {
      return s_to_time(ms_to_s(this[this.length()-1].timestamp - this[0].timestamp));
    }

    // distance stats
    distance_total() {
      return this[this.length()-1].distance_total;
    }

    distance_start_stop() {
      return calc_crow(this[0].latitude, this[0].longitude, this[this.length()-1].latitude, this[this.length()-1].longitude);
    }

    distance_max_from_start() {
      let distance_max = 0;
      let distance = 0;
      for(let i=1; i<this.length(); i++) {
        distance = calc_crow(this[0].latitude, this[0].longitude, this[i].latitude, this[i].longitude);
        if( distance > distance_max) {
          distance_max = distance;
        }
      }
      return distance_max;
    }

    // Horizontal speed stats
    average_speed() {
      let sum = 0;
      let count = 0;
      for(let i=0; i<this.length(); i++) {
        if( (this[i].speed > 0) || (count != 0) ) {
          count ++;
          sum += this[i].speed;
        }
      }
      return sum / count;
    }

    max_speed() {
      let speed = Object.values(this).map( point => point.speed);      
      return Math.max(...speed);
    }

    // Vertical speed stats
    average_vertical_speed() {
      let sum = 0;
      let count = 0;
      for(let i=0; i<this.length(); i++) {
        if( (this[i].vertical_speed > 0) || (count != 0) ) {
          count ++;
          sum += this[i].vertical_speed;
        }
      }
      return sum / count;
    }

    max_vertical_speed() {
      let vertical_speed = Object.values(this).map( point => point.vertical_speed);      
      return Math.max(...vertical_speed);
    }

    min_vertical_speed() {
      let vertical_speed = Object.values(this).map( point => point.vertical_speed);      
      return Math.min(...vertical_speed);
    }

    // Finesse moyenne

    // Elevation stats
    high() {
      return this[0].gpsAltitude - this[this.length()-1].gpsAltitude;
    }

    elevation_total() {
      let elevation_total = 0
      for(let i=1; i<this.length(); i++) {
        if(this[i].elevation > 0) {
          elevation_total += this[i].elevation;
        }
      }
      return elevation_total;
    }

    elevation_max() {
      let elevation = Object.values(this).map( point => point.gpsAltitude);      
      return Math.max(...elevation);
    }

    elevation_over_start() {
      let elevation_max = this.elevation_max();
      return(elevation_max - this[0].gpsAltitude);
    }

    // Position method
    get_positions_by_group(max_size) {
      let lon;
      let lat;
      let grp = -1;
      let ret = [];
      
      let i;
      for(i=0; i<this.length(); i++) {
        if(i%max_size == 0) {
          if(grp >= 0) {
            ret[grp] = lon + "&" + lat;
          }
          grp += 1;
          lon = "lon=" + this[i].longitude;
          lat = "lat=" + this[i].latitude;
        } else {
          lon += "|" + this[i].longitude;
          lat += "|" + this[i].latitude;
        }
      }
      if( ((i-1) % max_size) != 0 ) {
        ret[grp] = lon + "&" + lat;
      }
      return ret;
    }

    set_terrain_elevation(elevation_list) {
      for(let i=0; i<this.length(); i++) {
        this[i].terrain_elevation = elevation_list[i];
      }
    }
  }
  
  module.exports = {
    ParaglidingPoint
  };

},{}],3:[function(require,module,exports){
// browserify make_bundle.js -o client\bundle.js
var IGCParser = require('igc-parser');

var gpxParser = require('gpxparser');

var geoparagliding = require('./geoparagliding');

var flight = require('./flight');

window.IGCParser = IGCParser.parse;
window.gpxParser = gpxParser.gpxParser;
window.ParaglidingPoint = geoparagliding.ParaglidingPoint;
window.Flight = flight.Flight;

},{"./flight":1,"./geoparagliding":2,"gpxparser":6,"igc-parser":7}],4:[function(require,module,exports){
const MANUFACTURERS = require('.');

module.exports = function lookup(id) {
  let short = id.length === 1;

  id = id.toUpperCase();

  let manufacturers = MANUFACTURERS.filter(it => it[short ? 'short' : 'long'] === id);
  return manufacturers.length !== 0 ? manufacturers[0].name : id;
};

},{".":5}],5:[function(require,module,exports){
module.exports=[
  { "name": "Aircotec", "long": "ACT", "short": "I" },
  { "name": "Cambridge Aero Instruments", "long": "CAM", "short": "C" },
  { "name": "ClearNav Instruments", "long": "CNI", "short": null },
  { "name": "Data Swan/DSX", "long": "DSX", "short": "D" },
  { "name": "EW Avionics", "long": "EWA", "short": "E" },
  { "name": "Filser", "long": "FIL", "short": "F" },
  { "name": "Flarm", "long": "FLA", "short": "G" },
  { "name": "Flytech", "long": "FLY", "short": null },
  { "name": "Garrecht", "long": "GCS", "short": "A" },
  { "name": "IMI Gliding Equipment", "long": "IMI", "short": "M" },
  { "name": "Logstream", "long": "LGS", "short": null },
  { "name": "LX Navigation", "long": "LXN", "short": "L" },
  { "name": "LXNAV", "long": "LXV", "short": "V" },
  { "name": "Naviter", "long": "NAV", "short": null },
  { "name": "New Technologies", "long": "NTE", "short": "N" },
  { "name": "Nielsen Kellerman", "long": "NKL", "short": "K" },
  { "name": "Peschges", "long": "PES", "short": "P" },
  { "name": "PressFinish Electronics", "long": "PFE", "short": null },
  { "name": "Print Technik", "long": "PRT", "short": "R" },
  { "name": "Scheffel", "long": "SCH", "short": "H" },
  { "name": "Streamline Data Instruments", "long": "SDI", "short": "S" },
  { "name": "Triadis Engineering GmbH", "long": "TRI", "short": "T" },
  { "name": "Zander", "long": "ZAN", "short": "Z" },
  { "name": "XCSoar", "long": "XCS", "short": null },
  { "name": "LK8000", "long": "XLK", "short": null },
  { "name": "GpsDump", "long": "XGD", "short": null },
  { "name": "SeeYou Recorder", "long": "XCM", "short": null },
  { "name": "Flyskyhy", "long": "XFH", "short": null },
  { "name": "XCTrack", "long": "XCT", "short": null },
  { "name": "Flymaster Live", "long": "XFM", "short": null },
  { "name": "XCTracer", "long": "XTR", "short": null },
  { "name": "SkyBean", "long": "XSB", "short": null },
  { "name": "leGPSBip", "long": "XSD", "short": null },
  { "name": "Logfly", "long": "XLF", "short": null },
  { "name": "Loctome", "long": "XLM", "short": null }
]
},{}],6:[function(require,module,exports){
let gpxParser=function(){this.xmlSource="",this.metadata={},this.waypoints=[],this.tracks=[],this.routes=[]};gpxParser.prototype.parse=function(e){let t=this,l=new window.DOMParser;this.xmlSource=l.parseFromString(e,"text/xml");let r=this.xmlSource.querySelector("metadata");if(null!=r){this.metadata.name=this.getElementValue(r,"name"),this.metadata.desc=this.getElementValue(r,"desc"),this.metadata.time=this.getElementValue(r,"time");let e={},t=r.querySelector("author");if(null!=t){e.name=this.getElementValue(t,"name"),e.email={};let l=t.querySelector("email");null!=l&&(e.email.id=l.getAttribute("id"),e.email.domain=l.getAttribute("domain"));let r={},a=t.querySelector("link");null!=a&&(r.href=a.getAttribute("href"),r.text=this.getElementValue(a,"text"),r.type=this.getElementValue(a,"type")),e.link=r}this.metadata.author=e;let l={},a=this.queryDirectSelector(r,"link");null!=a&&(l.href=a.getAttribute("href"),l.text=this.getElementValue(a,"text"),l.type=this.getElementValue(a,"type"),this.metadata.link=l)}var a=[].slice.call(this.xmlSource.querySelectorAll("wpt"));for(let e in a){var n=a[e];let l={};l.name=t.getElementValue(n,"name"),l.sym=t.getElementValue(n,"sym"),l.lat=parseFloat(n.getAttribute("lat")),l.lon=parseFloat(n.getAttribute("lon"));let r=parseFloat(t.getElementValue(n,"ele"));l.ele=isNaN(r)?null:r,l.cmt=t.getElementValue(n,"cmt"),l.desc=t.getElementValue(n,"desc");let i=t.getElementValue(n,"time");l.time=null==i?null:new Date(i),t.waypoints.push(l)}var i=[].slice.call(this.xmlSource.querySelectorAll("rte"));for(let e in i){let l=i[e],r={};r.name=t.getElementValue(l,"name"),r.cmt=t.getElementValue(l,"cmt"),r.desc=t.getElementValue(l,"desc"),r.src=t.getElementValue(l,"src"),r.number=t.getElementValue(l,"number");let a=t.queryDirectSelector(l,"type");r.type=null!=a?a.innerHTML:null;let n={},o=l.querySelector("link");null!=o&&(n.href=o.getAttribute("href"),n.text=t.getElementValue(o,"text"),n.type=t.getElementValue(o,"type")),r.link=n;let u=[];var s=[].slice.call(l.querySelectorAll("rtept"));for(let e in s){let l=s[e],r={};r.lat=parseFloat(l.getAttribute("lat")),r.lon=parseFloat(l.getAttribute("lon"));let a=parseFloat(t.getElementValue(l,"ele"));r.ele=isNaN(a)?null:a;let n=t.getElementValue(l,"time");r.time=null==n?null:new Date(n),u.push(r)}r.distance=t.calculDistance(u),r.elevation=t.calcElevation(u),r.slopes=t.calculSlope(u,r.distance.cumul),r.points=u,t.routes.push(r)}var o=[].slice.call(this.xmlSource.querySelectorAll("trk"));for(let e in o){let l=o[e],r={};r.name=t.getElementValue(l,"name"),r.cmt=t.getElementValue(l,"cmt"),r.desc=t.getElementValue(l,"desc"),r.src=t.getElementValue(l,"src"),r.number=t.getElementValue(l,"number");let a=t.queryDirectSelector(l,"type");r.type=null!=a?a.innerHTML:null;let n={},i=l.querySelector("link");null!=i&&(n.href=i.getAttribute("href"),n.text=t.getElementValue(i,"text"),n.type=t.getElementValue(i,"type")),r.link=n;let s=[],p=[].slice.call(l.querySelectorAll("trkpt"));for(let e in p){var u=p[e];let l={};l.lat=parseFloat(u.getAttribute("lat")),l.lon=parseFloat(u.getAttribute("lon"));let r=parseFloat(t.getElementValue(u,"ele"));l.ele=isNaN(r)?null:r;let a=t.getElementValue(u,"time");l.time=null==a?null:new Date(a),s.push(l)}r.distance=t.calculDistance(s),r.elevation=t.calcElevation(s),r.slopes=t.calculSlope(s,r.distance.cumul),r.points=s,t.tracks.push(r)}},gpxParser.prototype.getElementValue=function(e,t){let l=e.querySelector(t);return null!=l?null!=l.innerHTML?l.innerHTML:l.childNodes[0].data:l},gpxParser.prototype.queryDirectSelector=function(e,t){let l=e.querySelectorAll(t),r=l[0];if(l.length>1){let l=e.childNodes;for(idx in l)elem=l[idx],elem.tagName===t&&(r=elem)}return r},gpxParser.prototype.calculDistance=function(e){let t={},l=0,r=[];for(var a=0;a<e.length-1;a++)l+=this.calcDistanceBetween(e[a],e[a+1]),r[a]=l;return r[e.length-1]=l,t.total=l,t.cumul=r,t},gpxParser.prototype.calcDistanceBetween=function(e,t){let l={};l.lat=e.lat,l.lon=e.lon;let r={};r.lat=t.lat,r.lon=t.lon;var a=Math.PI/180,n=l.lat*a,i=r.lat*a,s=Math.sin((r.lat-l.lat)*a/2),o=Math.sin((r.lon-l.lon)*a/2),u=s*s+Math.cos(n)*Math.cos(i)*o*o;return 6371e3*(2*Math.atan2(Math.sqrt(u),Math.sqrt(1-u)))},gpxParser.prototype.calcElevation=function(e){for(var t=0,l=0,r={},a=0;a<e.length-1;a++){let r=e[a+1].ele,n=e[a].ele;if(null!==r&&null!==n){let e=parseFloat(r)-parseFloat(n);e<0?l+=e:e>0&&(t+=e)}}for(var n=[],i=0,s=(a=0,e.length);a<s;a++){if(null!==e[a].ele){var o=parseFloat(e[a].ele);n.push(o),i+=o}}return r.max=Math.max.apply(null,n)||null,r.min=Math.min.apply(null,n)||null,r.pos=Math.abs(t)||null,r.neg=Math.abs(l)||null,r.avg=i/n.length||null,r},gpxParser.prototype.calculSlope=function(e,t){let l=[];for(var r=0;r<e.length-1;r++){let a=e[r],n=100*(e[r+1].ele-a.ele)/(t[r+1]-t[r]);l.push(n)}return l},gpxParser.prototype.toGeoJSON=function(){var e={type:"FeatureCollection",features:[],properties:{name:this.metadata.name,desc:this.metadata.desc,time:this.metadata.time,author:this.metadata.author,link:this.metadata.link}};for(idx in this.tracks){let r=this.tracks[idx];var t={type:"Feature",geometry:{type:"LineString",coordinates:[]},properties:{}};for(idx in t.properties.name=r.name,t.properties.cmt=r.cmt,t.properties.desc=r.desc,t.properties.src=r.src,t.properties.number=r.number,t.properties.link=r.link,t.properties.type=r.type,r.points){let e=r.points[idx];(l=[]).push(e.lon),l.push(e.lat),l.push(e.ele),t.geometry.coordinates.push(l)}e.features.push(t)}for(idx in this.routes){let r=this.routes[idx];t={type:"Feature",geometry:{type:"LineString",coordinates:[]},properties:{}};for(idx in t.properties.name=r.name,t.properties.cmt=r.cmt,t.properties.desc=r.desc,t.properties.src=r.src,t.properties.number=r.number,t.properties.link=r.link,t.properties.type=r.type,r.points){let e=r.points[idx];var l;(l=[]).push(e.lon),l.push(e.lat),l.push(e.ele),t.geometry.coordinates.push(l)}e.features.push(t)}for(idx in this.waypoints){let l=this.waypoints[idx];(t={type:"Feature",geometry:{type:"Point",coordinates:[]},properties:{}}).properties.name=l.name,t.properties.sym=l.sym,t.properties.cmt=l.cmt,t.properties.desc=l.desc,t.geometry.coordinates=[l.lon,l.lat,l.ele],e.features.push(t)}return e},"undefined"!=typeof module&&(require("jsdom-global")(),module.exports=gpxParser);
},{"jsdom-global":8}],7:[function(require,module,exports){
"use strict";
var lookupManufacturer = require('flight-recorder-manufacturers/lookup');
var ONE_HOUR = 60 * 60 * 1000;
var ONE_DAY = 24 * 60 * 60 * 1000;
/* tslint:disable:max-line-length */
var RE_A = /^A(\w{3})(\w{3,}?)(?:FLIGHT:(\d+)|\:(.+))?$/;
var RE_HFDTE = /^HFDTE(?:DATE:)?(\d{2})(\d{2})(\d{2})(?:,?(\d{2}))?/;
var RE_PLT_HEADER = /^H(\w)PLT(?:.{0,}?:(.*)|(.*))$/;
var RE_CM2_HEADER = /^H(\w)CM2(?:.{0,}?:(.*)|(.*))$/; // P is used by some broken Flarms
var RE_GTY_HEADER = /^H(\w)GTY(?:.{0,}?:(.*)|(.*))$/;
var RE_GID_HEADER = /^H(\w)GID(?:.{0,}?:(.*)|(.*))$/;
var RE_CID_HEADER = /^H(\w)CID(?:.{0,}?:(.*)|(.*))$/;
var RE_CCL_HEADER = /^H(\w)CCL(?:.{0,}?:(.*)|(.*))$/;
var RE_SIT_HEADER = /^H(\w)SIT(?:.{0,}?:(.*)|(.*))$/;
var RE_FTY_HEADER = /^H(\w)FTY(?:.{0,}?:(.*)|(.*))$/;
var RE_RFW_HEADER = /^H(\w)RFW(?:.{0,}?:(.*)|(.*))$/;
var RE_RHW_HEADER = /^H(\w)RHW(?:.{0,}?:(.*)|(.*))$/;
var RE_B = /^B(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(\d{3})([NS])(\d{3})(\d{2})(\d{3})([EW])([AV])(-\d{4}|\d{5})(-\d{4}|\d{5})/;
var RE_K = /^K(\d{2})(\d{2})(\d{2})/;
var RE_IJ = /^[IJ](\d{2})(?:\d{2}\d{2}[A-Z]{3})+/;
var RE_TASK = /^C(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(\d{4})([-\d]{2})(.*)/;
var RE_TASKPOINT = /^C(\d{2})(\d{2})(\d{3})([NS])(\d{3})(\d{2})(\d{3})([EW])(.*)/;
/* tslint:enable:max-line-length */
var VALID_DATA_SOURCES = ['F', 'O', 'P'];
var IGCParser = /** @class */ (function () {
    function IGCParser(options) {
        if (options === void 0) { options = {}; }
        this._result = {
            numFlight: null,
            pilot: null,
            copilot: null,
            gliderType: null,
            registration: null,
            callsign: null,
            competitionClass: null,
            loggerType: null,
            firmwareVersion: null,
            hardwareVersion: null,
            task: null,
            fixes: [],
            dataRecords: [],
            security: null,
            errors: [],
        };
        this.fixExtensions = [];
        this.dataExtensions = [];
        this.lineNumber = 0;
        this.prevTimestamp = null;
        this.options = options;
    }
    IGCParser.parse = function (str, options) {
        if (options === void 0) { options = {}; }
        var parser = new IGCParser(options);
        var errors = [];
        for (var _i = 0, _a = str.split('\n'); _i < _a.length; _i++) {
            var line = _a[_i];
            try {
                parser.processLine(line.trim());
            }
            catch (error) {
                if (options.lenient) {
                    errors.push(error);
                }
                else {
                    throw error;
                }
            }
        }
        var result = parser.result;
        result.errors = errors;
        return result;
    };
    Object.defineProperty(IGCParser.prototype, "result", {
        get: function () {
            if (!this._result.loggerManufacturer) {
                throw new Error("Missing A record");
            }
            if (!this._result.date) {
                throw new Error("Missing HFDTE record");
            }
            return this._result;
        },
        enumerable: false,
        configurable: true
    });
    IGCParser.prototype.processLine = function (line) {
        this.lineNumber += 1;
        var recordType = line[0];
        if (recordType === 'B') {
            var fix = this.parseBRecord(line);
            this.prevTimestamp = fix.timestamp;
            this._result.fixes.push(fix);
        }
        else if (recordType === 'K') {
            var data = this.parseKRecord(line);
            this.prevTimestamp = data.timestamp;
            this._result.dataRecords.push(data);
        }
        else if (recordType === 'H') {
            this.processHeader(line);
        }
        else if (recordType === 'C') {
            this.processTaskLine(line);
        }
        else if (recordType === 'A') {
            var record = this.parseARecord(line);
            this._result.loggerId = record.loggerId;
            this._result.loggerManufacturer = record.manufacturer;
            if (record.numFlight !== null) {
                this._result.numFlight = record.numFlight;
            }
        }
        else if (recordType === 'I') {
            this.fixExtensions = this.parseIJRecord(line);
        }
        else if (recordType === 'J') {
            this.dataExtensions = this.parseIJRecord(line);
        }
        else if (recordType === 'G') {
            this._result.security = (this._result.security || '') + line.slice(1);
        }
    };
    IGCParser.prototype.processHeader = function (line) {
        var headerType = line.slice(2, 5);
        if (headerType === 'DTE') {
            var record = this.parseDateHeader(line);
            this._result.date = record.date;
            if (record.numFlight !== null) {
                this._result.numFlight = record.numFlight;
            }
        }
        else if (headerType === 'PLT') {
            this._result.pilot = this.parsePilot(line);
        }
        else if (headerType === 'CM2') {
            this._result.copilot = this.parseCopilot(line);
        }
        else if (headerType === 'GTY') {
            this._result.gliderType = this.parseGliderType(line);
        }
        else if (headerType === 'GID') {
            this._result.registration = this.parseRegistration(line);
        }
        else if (headerType === 'CID') {
            this._result.callsign = this.parseCallsign(line);
        }
        else if (headerType === 'CCL') {
            this._result.competitionClass = this.parseCompetitionClass(line);
        }
        else if (headerType === 'SIT') {
            this._result.site = this.parseSite(line);
        }
        else if (headerType === 'FTY') {
            this._result.loggerType = this.parseLoggerType(line);
        }
        else if (headerType === 'RFW') {
            this._result.firmwareVersion = this.parseFirmwareVersion(line);
        }
        else if (headerType === 'RHW') {
            this._result.hardwareVersion = this.parseHardwareVersion(line);
        }
    };
    IGCParser.prototype.parseARecord = function (line) {
        var match = line.match(RE_A);
        if (match) {
            var manufacturer = lookupManufacturer(match[1]);
            var loggerId = match[2];
            var numFlight = match[3] ? parseInt(match[3], 10) : null;
            var additionalData = match[4] || null;
            return { manufacturer: manufacturer, loggerId: loggerId, numFlight: numFlight, additionalData: additionalData };
        }
        match = line.match(/^A(\w{3})(.+)?$/);
        if (match) {
            var manufacturer = lookupManufacturer(match[1]);
            var additionalData = match[2] ? match[2].trim() : null;
            return { manufacturer: manufacturer, loggerId: null, numFlight: null, additionalData: additionalData };
        }
        throw new Error("Invalid A record at line " + this.lineNumber + ": " + line);
    };
    IGCParser.prototype.parseDateHeader = function (line) {
        var match = line.match(RE_HFDTE);
        if (!match) {
            throw new Error("Invalid DTE header at line " + this.lineNumber + ": " + line);
        }
        var lastCentury = match[3][0] === '8' || match[3][0] === '9';
        var date = "" + (lastCentury ? '19' : '20') + match[3] + "-" + match[2] + "-" + match[1];
        var numFlight = match[4] ? parseInt(match[4], 10) : null;
        return { date: date, numFlight: numFlight };
    };
    IGCParser.prototype.parseTextHeader = function (headerType, regex, line, underscoreReplacement) {
        if (underscoreReplacement === void 0) { underscoreReplacement = ' '; }
        var match = line.match(regex);
        if (!match) {
            throw new Error("Invalid " + headerType + " header at line " + this.lineNumber + ": " + line);
        }
        var dataSource = match[1];
        if (VALID_DATA_SOURCES.indexOf(dataSource) === -1 && !this.options.lenient) {
            throw new Error("Invalid data source at line " + this.lineNumber + ": " + dataSource);
        }
        return (match[2] || match[3] || '').replace(/_/g, underscoreReplacement).trim();
    };
    IGCParser.prototype.parsePilot = function (line) {
        return this.parseTextHeader('PLT', RE_PLT_HEADER, line);
    };
    IGCParser.prototype.parseCopilot = function (line) {
        return this.parseTextHeader('CM2', RE_CM2_HEADER, line);
    };
    IGCParser.prototype.parseGliderType = function (line) {
        return this.parseTextHeader('GTY', RE_GTY_HEADER, line);
    };
    IGCParser.prototype.parseRegistration = function (line) {
        return this.parseTextHeader('GID', RE_GID_HEADER, line, '-');
    };
    IGCParser.prototype.parseCallsign = function (line) {
        return this.parseTextHeader('GTY', RE_CID_HEADER, line);
    };
    IGCParser.prototype.parseCompetitionClass = function (line) {
        return this.parseTextHeader('GID', RE_CCL_HEADER, line);
    };
    IGCParser.prototype.parseSite = function (line) {
        return this.parseTextHeader('SIT', RE_SIT_HEADER, line);
    };
    IGCParser.prototype.parseLoggerType = function (line) {
        return this.parseTextHeader('FTY', RE_FTY_HEADER, line);
    };
    IGCParser.prototype.parseFirmwareVersion = function (line) {
        return this.parseTextHeader('RFW', RE_RFW_HEADER, line);
    };
    IGCParser.prototype.parseHardwareVersion = function (line) {
        return this.parseTextHeader('RHW', RE_RHW_HEADER, line);
    };
    IGCParser.prototype.processTaskLine = function (line) {
        if (!this._result.task) {
            this._result.task = this.parseTask(line);
        }
        else {
            this._result.task.points.push(this.parseTaskPoint(line));
        }
    };
    IGCParser.prototype.parseTask = function (line) {
        var match = line.match(RE_TASK);
        if (!match) {
            throw new Error("Invalid task declaration at line " + this.lineNumber + ": " + line);
        }
        var lastCentury = match[3][0] === '8' || match[3][0] === '9';
        var declarationDate = "" + (lastCentury ? '19' : '20') + match[3] + "-" + match[2] + "-" + match[1];
        var declarationTime = match[4] + ":" + match[5] + ":" + match[6];
        var declarationTimestamp = Date.parse(declarationDate + "T" + declarationTime + "Z");
        var flightDate = null;
        if (match[7] !== '00' || match[8] !== '00' || match[9] !== '00') {
            lastCentury = match[9][0] === '8' || match[9][0] === '9';
            flightDate = "" + (lastCentury ? '19' : '20') + match[9] + "-" + match[8] + "-" + match[7];
        }
        var taskNumber = (match[10] !== '0000') ? parseInt(match[10], 10) : null;
        var numTurnpoints = parseInt(match[11], 10);
        var comment = match[12] || null;
        return {
            declarationDate: declarationDate,
            declarationTime: declarationTime,
            declarationTimestamp: declarationTimestamp,
            flightDate: flightDate,
            taskNumber: taskNumber,
            numTurnpoints: numTurnpoints,
            comment: comment,
            points: [],
        };
    };
    IGCParser.prototype.parseTaskPoint = function (line) {
        var match = line.match(RE_TASKPOINT);
        if (!match) {
            throw new Error("Invalid task point declaration at line " + this.lineNumber + ": " + line);
        }
        var latitude = IGCParser.parseLatitude(match[1], match[2], match[3], match[4]);
        var longitude = IGCParser.parseLongitude(match[5], match[6], match[7], match[8]);
        var name = match[9] || null;
        return { latitude: latitude, longitude: longitude, name: name };
    };
    IGCParser.prototype.parseBRecord = function (line) {
        if (!this._result.date) {
            throw new Error("Missing HFDTE record before first B record");
        }
        var match = line.match(RE_B);
        if (!match) {
            throw new Error("Invalid B record at line " + this.lineNumber + ": " + line);
        }
        var time = match[1] + ":" + match[2] + ":" + match[3];
        var timestamp = this.calcTimestamp(time);
        var latitude = IGCParser.parseLatitude(match[4], match[5], match[6], match[7]);
        var longitude = IGCParser.parseLongitude(match[8], match[9], match[10], match[11]);
        var valid = match[12] === 'A';
        var pressureAltitude = match[13] === '00000' ? null : parseInt(match[13], 10);
        var gpsAltitude = match[14] === '00000' ? null : parseInt(match[14], 10);
        var extensions = {};
        if (this.fixExtensions) {
            for (var _i = 0, _a = this.fixExtensions; _i < _a.length; _i++) {
                var _b = _a[_i], code = _b.code, start = _b.start, length = _b.length;
                extensions[code] = line.slice(start, start + length);
            }
        }
        var enl = null;
        if (extensions['ENL']) {
            var enlLength = this.fixExtensions.filter(function (it) { return it.code === 'ENL'; })[0].length;
            var enlMax = Math.pow(10, enlLength);
            enl = parseInt(extensions['ENL'], 10) / enlMax;
        }
        var fixAccuracy = extensions['FXA'] ? parseInt(extensions['FXA'], 10) : null;
        return {
            timestamp: timestamp,
            time: time,
            latitude: latitude,
            longitude: longitude,
            valid: valid,
            pressureAltitude: pressureAltitude,
            gpsAltitude: gpsAltitude,
            extensions: extensions,
            enl: enl,
            fixAccuracy: fixAccuracy,
        };
    };
    IGCParser.prototype.parseKRecord = function (line) {
        if (!this._result.date) {
            throw new Error("Missing HFDTE record before first K record");
        }
        if (!this.dataExtensions) {
            throw new Error("Missing J record before first K record");
        }
        var match = line.match(RE_K);
        if (!match) {
            throw new Error("Invalid K record at line " + this.lineNumber + ": " + line);
        }
        var time = match[1] + ":" + match[2] + ":" + match[3];
        var timestamp = this.calcTimestamp(time);
        var extensions = {};
        if (this.dataExtensions) {
            for (var _i = 0, _a = this.dataExtensions; _i < _a.length; _i++) {
                var _b = _a[_i], code = _b.code, start = _b.start, length = _b.length;
                extensions[code] = line.slice(start, start + length);
            }
        }
        return { timestamp: timestamp, time: time, extensions: extensions };
    };
    IGCParser.prototype.parseIJRecord = function (line) {
        var match = line.match(RE_IJ);
        if (!match) {
            throw new Error("Invalid " + line[0] + " record at line " + this.lineNumber + ": " + line);
        }
        var num = parseInt(match[1], 10);
        if (line.length < 3 + num * 7) {
            throw new Error("Invalid " + line[0] + " record at line " + this.lineNumber + ": " + line);
        }
        var extensions = new Array(num);
        for (var i = 0; i < num; i++) {
            var offset = 3 + i * 7;
            var start = parseInt(line.slice(offset, offset + 2), 10) - 1;
            var end = parseInt(line.slice(offset + 2, offset + 4), 10) - 1;
            var length = end - start + 1;
            var code = line.slice(offset + 4, offset + 7);
            extensions[i] = { start: start, length: length, code: code };
        }
        return extensions;
    };
    IGCParser.parseLatitude = function (dd, mm, mmm, ns) {
        var degrees = parseInt(dd, 10) + parseFloat(mm + "." + mmm) / 60;
        return (ns === 'S') ? -degrees : degrees;
    };
    IGCParser.parseLongitude = function (ddd, mm, mmm, ew) {
        var degrees = parseInt(ddd, 10) + parseFloat(mm + "." + mmm) / 60;
        return (ew === 'W') ? -degrees : degrees;
    };
    /**
     * Figures out a Unix timestamp in milliseconds based on the
     * date header value, the time field in the current record and
     * the previous timestamp.
     */
    IGCParser.prototype.calcTimestamp = function (time) {
        var timestamp = Date.parse(this._result.date + "T" + time + "Z");
        // allow timestamps one hour before the previous timestamp,
        // otherwise we assume the next day is meant
        while (this.prevTimestamp && timestamp < this.prevTimestamp - ONE_HOUR) {
            timestamp += ONE_DAY;
        }
        return timestamp;
    };
    return IGCParser;
}());
module.exports = IGCParser;

},{"flight-recorder-manufacturers/lookup":4}],8:[function(require,module,exports){
/*
 * this is what browserify will use if you use browserify on your tests.
 * no need to bootstrap a DOM environment in a browser.
 */

module.exports = function () {
  return noop
}

function noop () { }

},{}]},{},[3]);
