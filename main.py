from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from xml.dom import minidom
import math
import re

kmlns = "http://www.opengis.net/kml/2.2"

def parse_route_string(routestr):
    airports = routestr.split('-')
    c = re.compile('^[A-Z]{3}$')
    if not all((c.match(x) for x in airports)):
        raise Exception("Illegal route string")

    if len(airports) < 2:
        raise Exception("Route too short, need at least 2 airports")

    return airports

def get_airports():
    dom = minidom.parse(open("airports.kml"))
    airportdb = {}
    for node in dom.getElementsByTagNameNS(kmlns, 'description'):
        desc = dict([x.split(' : ', 1) for x in
                     node.childNodes[0].nodeValue.strip().split('\n')])
        airportdb[desc['code']] = desc
    return airportdb

def gc_distance(airportdb, start, end):
    desc1 = airportdb[start]
    desc2 = airportdb[end]
    lat1 = float(desc1['lat'])
    lon1 = float(desc1['lon'])
    lat2 = float(desc2['lat'])
    lon2 = float(desc2['lon'])

    dlat = lat1 - lat2
    dlon = lon1 - lon2

    dlat = math.radians(dlat)
    dlon = math.radians(dlon)

    # Haversine formula
    a = (math.sin(dlat/2) * math.sin(dlat/2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon/2) * math.sin(dlon/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a));
    return 3958.75587 * c;


class MainPage(webapp.RequestHandler):
    def post(self):
        self.get()
        route = self.request.get("r")
        milesmin500 = 0
        miles = 0
        try:
            airports = parse_route_string(route)
            airportdb = get_airports()
            line = "%s (%s, %s) => %s (%s, %s) (%d miles)<br/>"
            for i in range(1, len(airports)):
                a1 = airportdb[airports[i - 1]]
                a2 = airportdb[airports[i]]
                distance = int(gc_distance(airportdb, a1['code'], a2['code']))
                miles += distance
                # min 500 miles per leg
                milesmin500 += max(500, distance)
                leg = line % (a1['code'], a1['lat'], a1['lon'],
                              a2['code'], a2['lat'], a2['lon'],
                              distance)
                self.response.out.write(leg)
            if (milesmin500 > miles):
                self.response.out.write("Total: %d (%d)" % (miles, milesmin500))
            else:
                self.response.out.write("Total: %d" % miles)
        except Exception, e:
            self.response.out.write(e)

    def get(self):
        self.response.out.write("""
          <html>
            <body>
              <form action="/" method="post">
                Enter a route (e.g. SFO-LAX-JFK)<br/>
                <input type="text" name="r">
                <input type="submit">
                <a href="/gm/ita_mileage.user.js">Get mileage on ITA</a>
              </form>
            </body>
          </html>""")


class ApiHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        if (not self.request.path.startswith('/api/')):
            raise Exception("Illegal path")

        miles = 0
        try:
            airports = parse_route_string(self.request.path[5:])
            airportdb = get_airports()
            for i in range(1, len(airports)):
                code1 = airports[i - 1]
                code2 = airports[i]
                miles += int(gc_distance(airportdb, code1, code2))
        except KeyError, ke:
            self.response.out.write("Illegal airport code ")
            self.response.out.write(ke)
            return
        except Exception, e:
            self.response.out.write(e)
            return

        self.response.out.write('%d miles' % (miles))


application = webapp.WSGIApplication([('/', MainPage),
                                      ('/api/.*', ApiHandler)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
