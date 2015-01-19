var infowindow = new google.maps.InfoWindow({
  content: ""
});

function addMarker(lat, lng, map, concert){
  var latlng = new google.maps.LatLng(lat,lng);
  var marker = new google.maps.Marker({
    position: latlng,
    map: map
  });

  var track = '';
  function set_track() {
    return concert.tracks[0].sc_track_id;
  };
  track = set_track();

  var artist = '';
  function set_artist() {
    return concert.artists['py/seq'][0].name;
  };
  artist = set_artist();

  var venue = '';
  function set_venue() {
    return concert.venue.name;
  };
  venue = set_venue();

  var event_url = concert.event_url;

  google.maps.event.addListener(marker, 'click', function() {
    infowindow.setContent('<div class="eventinfo"><a href="' + event_url + '"><art>'+ artist + '</art><br> playing at <ven>' + venue + '</ven><br> on <dat>' + concert.event_date + '</dat></a></div><iframe width="100%" height="166" scrolling="no" frameborder="no" src="https://w.soundcloud.com/player/?url=http%3A%2F%2Fapi.soundcloud.com%2Ftracks%2F'+
                          track
                          + '"></iframe>');
    infowindow.open(map,marker);
  });
  return marker;
};

google.maps.Map.prototype.clearOverlays = function() {
  for (var i = 0; i < markersArray.length; i++ ) {
    markersArray[i].setMap(null);
  }
}

var geocoder;
var map;
var markers = [];

function initialize() {
  $.ajaxSetup ({  
    cache: false  
  });
  var lat;
  var lng;
  var zipcode;
  if (google.loader.ClientLocation){
    lat = google.loader.ClientLocation.latitude;
    lng = google.loader.ClientLocation.longitude;
    zipcode = google.loader.ClientLocation.address.zipcode;
  } else {
    lat = 39.951673;
    lng =-75.191287;
    zipcode = 19103;
  }
  var mapOptions = {
    center: new google.maps.LatLng(lat, lng),
    zoom: 10,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  map = new google.maps.Map(document.getElementById("map_canvas"),
                            mapOptions);

  geocoder = new google.maps.Geocoder();
  
  $.getJSON("/update", {"lat": lat, "lng": lng}, update_pins);  

  var btns_day = ['day-one', 'day-two', 'day-thr'];
  var input_day = document.getElementById('btn-input-day');
  for(i = 0; i < btns_day.length; i++) {
    document.getElementById(btns_day[i]).addEventListener('click', function() {
      for (var j=0; j<btns_day.length; j++) {
        if (j!==i) {
          document.getElementById(btns_day[j]).className="btn";
        }
      }
      input_day.value = this.value;
      this.className="btn active";
      $.getJSON("/update", {"day": this.value}, update_pins);
    });
  }  
  var btns = ['btn-one', 'btn-two', 'btn-thr'];
  var input = document.getElementById('btn-input');
  for(var i = 0; i < btns.length; i++) {
    document.getElementById(btns[i]).addEventListener('click', function() {
      for (var j=0; j<btns.length; j++) {
        if (j!==i) {
          document.getElementById(btns[j]).className="btn";
        }
      }
      input.value = this.value;
      this.className="btn active";
      $.getJSON("/update", {"radius": this.value},
                update_pins
               );
    });
  }

  $("#address").keypress(function (e) {
    if (e.keyCode == 13) {
      e.preventDefault();
      $(this).blur();
      codeAddress();
      //$.getJSON("/update", {"address": this.value}, update_pins);
      this.value = document.getElementById('address').value;
      return false;
    }
  });
};

function codeAddress() {
  var address = document.getElementById('address').value;
  geocoder.geocode( { 'address': address}, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      map.setCenter(results[0].geometry.location);
    } else {
      alert('Geocode was not successful for the following reason: ' + status);
    }
  });
  this.className="btn active";
  var request = $.getJSON("/update",
                          {"address": address},
                          update_pins
                         );
};

Array.prototype.remove = function(from, to) {
  var rest = this.slice((to || from) + 1 || this.length);
  this.length = from < 0 ? this.length + from : from;
  return this.push.apply(this, rest);
};

function update_pins(data) {
  for (var i = 0; i < markers.length; i++) {
    var index = data.indexOf(markers[i]); 
    if (index == -1)
      markers[i].setMap(null);
    else {
      data.remove(index);
    }
  }
  for (var i = 0; i < data.length; i++) {
    markers.push(addMarker(data[i].venue.lat, 
                           data[i].venue.lng, map, data[i]));
  }
};