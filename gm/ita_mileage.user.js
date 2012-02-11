// ==UserScript==
// @name           Mileage Finder
// @namespace      http://routemiles.appspot.com
// @description    Show miles on flights
// @include        http://matrix.itasoftware.com/*
// ==/UserScript==

function showMiles(row) {
  return function(resp) {
    row.innerHTML = row.innerHTML + resp.responseText;
  };
}

function populate() {
  var solutions = document.getElementsByClassName('itaSolutionRow');
  if (solutions.length > 0) {
    clearInterval(pop);
  } else {
    return;
  }
  for (var i = 0; i < solutions.length; ++i) {
    var row = solutions[i];
    rounds = row.getElementsByClassName('itaSliceAirports').length;

    for (var a = 0; a < rounds; a++) {
      var endpoints = row.getElementsByClassName('itaSliceAirports')[a].getElementsByClassName("tooltip");
      var stops = row.getElementsByClassName('itaSliceStops')[a].getElementsByClassName("tooltip");
      var tar = row.getElementsByClassName('dijitReset itaSliceDuration')[a];
      var route = [];
      route.push(endpoints[0].innerHTML);
      for (var j = 0; j < stops.length; ++j) {
        route.push(stops[j].innerHTML);
      }
      route.push(endpoints[1].innerHTML);
      var url = "http://routemiles.appspot.com/api/"
      var routestr = route[0];
      for (var r = 1; r < route.length; ++r) {
        routestr += '-' + route[r];
      }
      url += routestr;
      GM_xmlhttpRequest({method: "GET", url: url, onload: showMiles(tar)});
    }
  }
}

var pop = setInterval(populate, 1000);
