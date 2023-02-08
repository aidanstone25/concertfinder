from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

#TODO all id's have a fixed length, don't just put random lengths
#TODO have to delete these things when the date expires 
class Concert(db.Model):
    concert_id = db.Column(db.String(50), primary_key=True)
    concert_name = db.Column(db.String(100))
    concert_image = db.Column(db.String(100))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    dist = db.Column(db.Float)
    city = db.Column(db.String(200))
    venue = db.Column(db.String(200))
    min_price = db.Column(db.Float) 
    max_price = db.Column(db.Float) 
    #TODO should i convert to actual datetime object, ticketpy has it as string but might be smart to concert cause deprication
    date = db.Column(db.String(55))
    concert_artist = db.Column(db.String(100), db.ForeignKey('artist.artist_id'))
    concert_website_link = db.String(db.String(200))
    user_id = db.Column(db.String(100), db.ForeignKey('user.spotify_user_id'))


class Artist(db.Model):
    artist_id = db.Column(db.String(100), primary_key=True)
    artist = db.Column(db.String(1000))
    user_id = db.Column(db.String(1000), db.ForeignKey('user.spotify_user_id'),primary_key=True)
    concerts = db.relationship('Concert')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    spotify_user_id = db.Column(db.String(1000),unique=True)
    #TODO user = User.query.filter_by(spotify_user_id=signed_in_user['id']).first()  no such col user.longitude
    longitude = db.Column(db.Integer, default=None)
    latitude = db.Column(db.Integer,default=None)
    location_name = db.Column(db.String(200),default=None)
    phone_number = db.Column(db.Integer,default=None)
    email = db.Column(db.String(50),default=None)
    artist = db.relationship('Artist')
    Albums = db.relationship('Albums')
    concerts = db.relationship('Concert')

#TODO delete
class Albums(db.Model):
    album_id = db.Column(db.String(100),primary_key=True)
    album = db.Column(db.String(100))
    artist = db.Column(db.String(100))
    artist_id = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    album_cover_link = db.Column(db.String(50))
    album_rating = db.Column(db.Integer)
    spotify_user_id = db.Column(db.String(10000), db.ForeignKey('user.spotify_user_id'),primary_key=True)
    popularity = db.Column(db.Integer)

#TODO prob delete
class Location(db.Model):
    spotify_user_id = db.Column(db.String(10000), db.ForeignKey('user.spotify_user_id'),primary_key=True)
    location_name = db.Column(db.String(200),primary_key=True)
    longitude = db.Column(db.Integer)
    latitude = db.Column(db.Integer)
    acceptable_radius = db.Column(db.Integer)