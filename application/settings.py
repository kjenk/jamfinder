import settings_private

APPLICATION_URL = "http://www.jamfinder.com"

# API
GOOGLE_MAPS_API_KEY = settings_private.GOOGLE_MAPS_API_KEY
GOOGLE_MAPS_API_URL = "http://maps.google.com/maps/geo?key=%s" % GOOGLE_MAPS_API_KEY
GOOGLE_GEOCODE_API_URL = ('http://maps.googleapis.com/maps/api/geocode/json?')
API_RETRIES = 10
SOUNDCLOUD_API_URL = "http://api.soundcloud.com"
SOUNDCLOUD_TIMEZONE_ADJUSTMENT = 0 # in hours behind server timezone
SOUNDCLOUD_CONSUMER_KEY = settings_private.SOUNDCLOUD_CLIENT_ID
DURATION_LIMIT = "1200000" # in milliseconds to filter out dj-sets + podcasts
JAMBASE_API_KEY = settings_private.JAMBASE_API_KEY
JAMBASE_API_URL = 'http://api.jambase.com/search?apikey=%s&' % JAMBASE_API_KEY
JAMBASE_ARTIST_URL = 'http://www.jambase.com/Artists/Artist.aspx?'
JAMBASE_EVENT_URL = 'http://www.jambase.com/shows/event.aspx?'
MAX_SONG_NUM = 1
DEFAULT_ZIPCODE = 19104

# Frontend
FRONTEND_LOCATIONS_LIMIT = 200 # How many locations shall be displayed as default in FrontEnd?
MAX_TRACKS_CACHE_TIME = 30 # How long in minutes are the max tracks counters going to be cached?

# Backend
CLEANUP_INTERVAL = 2 # How old can oldest track be (in minutes)
API_QUERY_INTERVAL = 6 # In which Interval in minutes is the backend scripts /backend-update called?
TRACK_BACKEND_UPDATE_LIFETIME = 60 # How long in minutes shall a track remain in Taskqueue/Memcache before purged if not copmpleted?
