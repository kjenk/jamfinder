from sqlalchemy import (Table, Column, Integer, String,
                        DateTime, Float, ForeignKey)
import config
from sqlalchemy.ext.declarative import declarative_base
from application import db

Base = declarative_base()

class DateTimeExt(DateTime):
    def __init__(self, *args, **kwargs):
        super(DateTimeExt, self).__init__(*args, **kwargs)
    def __repr__(self):
        return self.strftime('%m/%d/%y')

class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(Integer, primary_key = True)
    name = db.Column(String(30))
    jambase_artist_id = db.Column(Integer, unique = True, index = True)
    sc_user_id = db.Column(String(30), unique = True, index = True)
    url = db.Column(String(30), unique = True)
    tracks = db.relationship('Track', backref='artist',
                             lazy='dynamic')

    def __init__(self, jambase_artist_id, name, url, sc_artist_id = None):
        self.sc_user_id = sc_artist_id
        self.name = name
        self.url = url
        self.jambase_artist_id = jambase_artist_id

    def __repr__(self):
        return "[Artist: %s %s %s]" % (self.sc_user_id, self.name, self.url)

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(Integer, primary_key=True)
    jambase_venue_id = db.Column(Integer, unique = True, index = True)
    name = db.Column(String(30), unique = False)
    city = db.Column(String(30), unique = False)
    address = db.Column(String(50), unique = False)
    state = db.Column(String(50), unique = False)
    zipcode = db.Column(Integer, unique = False)
    lat = db.Column(Float, unique = False)
    lng = db.Column(Float, unique = False)

    def __init__(self, jambase_venue_id, name, lat, lng,
                 city, address, state, zipcode):
        self.jambase_venue_id = jambase_venue_id
        self.name = name
        self.lat = lat
        self.lng = lng
        self.city = city
        self.zipcode = zipcode
        self.address = address
        self.state = state

    def __repr__(self):
        return "[venue: %s %s %s %s]" %(self.name, self.city, self.zipcode, self.state)

class Track(db.Model):
    __tablename__ = 'track'
    id = db.Column(Integer, primary_key = True)
    sc_track_id = db.Column(String(30), unique = True, index = True)
    sc_user_id = db.Column(Integer, db.ForeignKey('artist.sc_user_id'),
                           index = True)
    purchase_url = db.Column(String(120))
    artwork_url = db.Column(String(120))
    genre = db.Column(String(50))

    def __init__(self, sc_track_id, sc_user_id, purchase_url, artwork_url, genre):
        self.sc_track_id = sc_track_id
        self.sc_user_id = sc_user_id
        self.purchase_url = purchase_url
        self.artwork_url = artwork_url
        self.genre = genre

    def to_dict(self):
        return {'sc_track_id':self.sc_track_id, 'sc_user_id': self.sc_user_id,
                'purchase_url':self.purchase_url, 'artwork_url': self.artwork_url,
                'genre':self.genre}

    def __repr__(self):
        return "%s %s %s %s %s" % (self.sc_track_id, self.sc_user_id, self.purchase_url,
                                   self.artwork_url, self.genre)

association_table = db.Table('association',
                        db.Column('event_id', Integer, ForeignKey('event.id')),
                        db.Column('artist_id', Integer, ForeignKey('artist.id')))

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(Integer, primary_key=True)
    jambase_event_id = db.Column(Integer, unique=True, index = True)
    artists = db.relationship('Artist', secondary = association_table,
                              backref=db.backref('events',
                                                 lazy='dynamic'))
    event_date = db.Column(DateTimeExt, unique=False)
    jambase_venue_id = Column(Integer, ForeignKey('venue.jambase_venue_id'),
                              index = True)
    venue = db.relationship("Venue")
    event_url = db.Column(String)
    zipcode = db.Column(Integer, index = True)

    def __init__(self, event_id, event_date, jambase_venue_id, event_url, zipcode):
        self.jambase_event_id = event_id
        self.event_date = event_date
        self.jambase_venue_id = jambase_venue_id
        self.event_url = event_url
        self.zipcode = zipcode

    def __repr__(self):
        return "%s %s %s %s %s" % (self.jambase_event_id, str(self.artists),
                                   self.event_date,
                                   self.venue, self.event_url)

class PrevRequest(db.Model):
    __tablename__ = 'prev_request'
    id = db.Column(db.Integer, primary_key=True)
    zipcode = db.Column(Integer, unique=True)
    radius = db.Column(Integer, unique=True)
    date = db.Column(DateTime)

    def __init__(self, zipcode, radius, date):
        self.zipcode = zipcode
        self.radius = radius
        self.date = date

    def __repr__(self):
        return "%s %s %s" % (self.zipcode, self.radius, self.date)
