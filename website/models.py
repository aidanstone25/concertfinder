from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

#TODO all id's have a fixed length, don't just put random lengths

class Concert(db.Model):
    concert_id = db.Column(db.Integer, primary_key=True)
    concert_image = db.String(db.String(500))
    longitude = db.Column(db.Integer)
    latitude = db.Column(db.Integer)
    location_name = db.Column(db.String(200))
    #TODO sinking suspicion this won't work lol
    date = db.Column(db.DateTime(timezone=True))
    concert_artist = db.Column(db.String(100), db.ForeignKey('artist.artist_id'))

    addtional_performers = db.String(db.String(500))
    concert_website_link = db.String(db.String(200))

class Artist(db.Model):
    artist_id = db.Column(db.String(100), primary_key=True)
    artist = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.spotify_user_id'))
    concerts = db.relationship('Concert')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    spotify_user_id = db.Column(db.String(10000),unique=True)
    phone_number = db.Column(db.Integer)
    email = db.Column(db.String(50))
    artist = db.relationship('Artist')
    Albums = db.relationship('Albums')

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

class Location(db.Model):
    spotify_user_id = db.Column(db.String(10000), db.ForeignKey('user.spotify_user_id'),primary_key=True)
    location_name = db.Column(db.String(200),primary_key=True)
    longitude = db.Column(db.Integer)
    latitude = db.Column(db.Integer)
    acceptable_radius = db.Column(db.Integer)