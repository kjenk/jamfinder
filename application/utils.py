import json
import logging
import time
from models import *
import settings
import urllib2, urllib
import soundcloud
from datetime import datetime, date
import cgi
from flask import json
from bs4 import BeautifulSoup
import jsonpickle
import operator
from fuzzywuzzy import fuzz

def get_soup(url):
  try:
    req = urllib2.Request(url)
  except urllib2.HTTPError:
    pass
  return BeautifulSoup(urllib2.urlopen(req).read())

def parse_xml_response(content, **kwargs):
  tree = BeautifulSoup(content)
  events = []
  for event in tree('event'):
    jambase_event_id = int(event.find('event_id').text)
    db_event_record = Event.query.filter_by(jambase_event_id=jambase_event_id).first()
    if not db_event_record:
      venue = event.find('venue')
      venue_id = int(venue.find('venue_id').text)
      db_event_record = Event(jambase_event_id,
                              datetime.strptime(event.find('event_date').text,
                                                '%m/%d/%Y'), venue_id,
                              event.find('event_url').text, kwargs['zipcode'])
      for artist in event('artists'):
        artist_id = int(artist.find('artist_id').text)
        db_artist_record = Artist.query.filter_by(jambase_artist_id = artist_id).first()
        if not db_artist_record:
          db_artist_record = Artist(artist_id, artist.find('artist_name').text, None)
          db_event_record.artists.append(db_artist_record)
          db.session.add(db_artist_record)
      db_venue_record = Venue.query.filter_by(jambase_venue_id=venue_id).first()
      print db_venue_record, venue_id
      if not db_venue_record:
        venue_name = venue.find('venue_name').text
        venue_city = venue.find('venue_city').text
        venue_state = venue.find('venue_state').text
        venue_zip = int(venue.find('venue_zip').text)
        venue_address = get_address(event.find('event_id').text)
        (lat, lng) = get_latlng(venue_address)
        db_venue_record = Venue(venue_id, venue_name, lat, lng, venue_city,
                          venue_address, venue_state, venue_zip)
        db.session.add(db_venue_record)
        db.session.commit()
      db.session.add(db_event_record)
    events.append(db_event_record)
  db.session.commit()
  return events

def open_remote_api(query, api, **kwargs):
  """
  Calls a remote API with a query. Returns json.
  Google App Enging sometimes fails to open the URL properly resulting in a DownloadError.
  So we have to do it more often sometimes ...
  """
  if api == "googlemaps":
    api_url = settings.GOOGLE_MAPS_API_URL
    api_name = "Google Maps API"
  if api == 'geocode':
    api_url = settings.GOOGLE_GEOCODE_API_URL
    api_name = "Google Geocode API"
  if api == "jambase":
    api_url = settings.JAMBASE_API_URL
    api_name = 'Jambase API'
  query = api_url + query
  logging.info("Requesting %s with uri: %s" % (api_name, query))
  i = 0
  while True:
    if (i >= settings.API_RETRIES):
      break
    try:
      req = urllib2.Request(query)
      result = urllib2.urlopen(req).read()
      i = 0
      break
    except Exception:
      pass
    i += 1
  if i != 0:
    logging.error("Connection to %s failed." % api_name)
    raise Exception("Connection to %s failed." % api_name)
  logging.info("Result for %s Query: %s" % (api_name, result))
  if api == 'jambase':
    return parse_xml_response(result, **kwargs)
  else:
    return json.loads(result)

def canonical_url(u):
  u = u.lower()
  if u.startswith("http://"):
    u = u[7:]
  if u.startswith("www."):
    u = u[4:]
  if u.endswith("/"):
    u = u[:-1]
    return u

def get_official_website(jambase_artist_id):
  url = settings.JAMBASE_ARTIST_URL + 'ArtistID=%s' %jambase_artist_id
  result = get_soup(url).find_all("a", text='Official Website')
  if len(result) > 0 :
    return canonical_url(result[0]['href'])
  else:
    return None

def get_address(jambase_event_id):
  url = settings.JAMBASE_EVENT_URL + 'eventid=%s' %jambase_event_id
  soup = get_soup(url)
  street_address = soup.find_all("dd", class_="streetAddress")[0].contents[-1].strip()
  city_address = soup.find_all("dd", class_="cityAddress")[0].text.strip()
  address = "%s %s" %(street_address, city_address)
  return address

def get_soundcloud_id(client, artist):
  artists = client.get('/users', q=artist.name)
  if len(artists) == 0:
    return None
  artist_fuzzs = [(x, fuzz.token_set_ratio(artist.name,
                                               x.username)) for x in artists]
  max_artist = max(artist_fuzzs, key = operator.itemgetter(1))
  if max_artist[1] > 85:
    artist.sc_user_id = max_artist[0].id
    return max_artist[0].id
  else:
    return None

def fetch_concert_info(zipcode, radius, start_date,
                       end_date, num_result):
  zipcode = "zip=%s" % zipcode if zipcode else ""
  start_date = "startDate=%s" % start_date.strftime('%m/%d/%y') if start_date else ""
  end_date = "endDate=%s" % end_date.strftime('%m/%d/%y') if end_date else ""
  radius = "radius=%s" % radius if radius else ""
  num_result = "n=%d" % num_result if num_result else ""
  params = [zipcode, start_date, end_date, radius, num_result]
  query_string  = "&".join(filter (lambda x :len(x) >0, params))
  return open_remote_api(query_string, 'jambase', zipcode=zipcode)

def to_db_track_record_list(tracks):
  artist_tracks = []
  for track in tracks:
    db_track_record = Track.query.filter_by(sc_track_id = track.id).first()
    if not db_track_record:
      db_track_record = Track(int(track.id), int(track.user_id), track.purchase_url,
                              track.artwork_url, track.genre)
      artist_tracks.append(db_track_record)
  print "number of songs fetched :", len(artist_tracks)
  return artist_tracks

def get_artist_tracks(client, artist, limit = settings.MAX_SONG_NUM):
  print "artist sound_cloud request start ", artist.name
  tracks = client.get('/users/%s/tracks' % artist.id, limit = limit,
                      order='hotness')
  print "sound_cloud request end"
  return to_db_track_record_list(tracks)

def get_tracks(client, artist, limit = settings.MAX_SONG_NUM):
  #print "tracks sound_cloud request start ", artist.id
  tracks = client.get('/tracks', q=artist.name, order='hotness',
                      limit = limit)
  #print "sound_cloud request end"
  return to_db_track_record_list(tracks)

def get_latlng(address):
  query_string='&%s' % urllib.urlencode({'address':address, 'sensor':'true'})
  response = open_remote_api(query_string, 'geocode')
  loc = response[unicode('results')][0][unicode('geometry')][unicode('location')]
  return (loc[unicode('lat')], loc[unicode('lng')])

def deg2rad(deg):
  return deg * (math.pi/180)

#gives distance in miles
def get_distance_lat_lon(lat1, lon1, lat2, lon2):
  R = 6371 # Radius of the earth in km
  dLat = deg2rad(lat2-lat1)
  dLon = deg2rad(lon2-lon1)
  a = (math.sin(dLat/2) * math.sin(dLat/2) +
  math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) *
  math.sin(dLon/2) * math.sin(dLon/2))
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
  d = R * c
  return d * 0.621371 #convert back to miles

def get_zipcode_from_address(address):
  query_string='&%s' % urllib.urlencode({'address':address, 'sensor':'true'})
  response = open_remote_api(query_string, 'geocode')
  postal_obj = response[unicode('results')][0][unicode('address_components')][-1]
  if postal_obj[unicode('types')][0] == 'postal_code':
    return postal_obj[unicode('long_name')]
  else:
    loc = response[unicode('results')][0][unicode('geometry')][unicode('location')]
    return get_zipcode_from_latlng(loc[unicode('lat')], loc[unicode('lng')])

def get_zipcode_from_latlng(lat, lng):
    query_string='&%s' % urllib.urlencode({'latlng':'%s,%s'
                                           %(lat, lng),
                                           'sensor':'true'})
    response = open_remote_api(query_string, 'geocode')
    postal_obj = response[unicode('results')][0][unicode('address_components')][-1]
    if postal_obj['types'][0] == 'postal_code':
      return postal_obj[unicode('long_name')]

def get_concert_songs(zipcode, radius=100, start_date = date.today(),
                      end_date = None, num_result = 40):
  db_prev_request = PrevRequest.query.filter_by(zipcode = int(zipcode), radius=radius,
                                          date=end_date).first()
  #print db_prev_request
  radius = radius or 100
  start_date = start_date or date.today()
  now = datetime.now()
  client = soundcloud.Client(client_id=settings.SOUNDCLOUD_CONSUMER_KEY)
  concerts = fetch_concert_info(zipcode, radius, start_date, end_date, num_result)
  concert_result = []
  print "len concerts ", len(concerts)
  for concert in concerts:
    db_track_records = []
    for artist in concert.artists:
      soundcloud_id = get_soundcloud_id(client, artist)
      if soundcloud_id:
        db_track_records = Track.query.filter_by(sc_user_id =
                                                 soundcloud_id).limit(1).all()
        db_artist_records = Artist.query.filter_by(sc_user_id =
                                                   soundcloud_id).limit(1).all()
        print "db_track_records", db_track_records
      if len(db_track_records) == 0 and len(db_artist_records) == 0:
        if not soundcloud_id:
          db_track_records.extend(get_tracks(client, artist))
        else:
          db_track_records.extend(get_artist_tracks(client, artist))
        for track in db_track_records:
          db.session.add(track)
          artist.tracks.append(track)
        db.session.commit()
    if len(db_track_records) > 0:
      concert.tracks = map(operator.methodcaller('to_dict'), db_track_records)
      concert_result.append(concert)
  print "length of final result ", len(concert_result)
  return jsonpickle.encode(concert_result)

if __name__=="__main__":
        # print fetch_concert_info(19104)
  # client = soundcloud.Client(client_id=settings.SOUNDCLOUD_CONSUMER_KEY)
  # print get_users(client, '')
  # print get_location('3900 chestnut street philadelphia')
  print get_zipcode_from_latlng(39.879, -74.897)
  print get_zipcode_from_address("san francisco ca")
  #print get_concert_songs(10004)
