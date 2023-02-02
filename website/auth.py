import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, url_for, session, request, redirect, flash,render_template,Blueprint
import json
import time
import pandas as pd
from flask_login import login_user, logout_user,current_user
from . import db
from . models import User,Artist
import ticketpy



auth = Blueprint('auth', __name__)

#spotify auth, creates local account for database
@auth.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    signed_in_user=sp.current_user()
    user = User.query.filter_by(spotify_user_id=signed_in_user['id']).first()
    if user:
        login_user(user=user,remember=True)
    else:
        new_user = User(spotify_user_id=signed_in_user['id'])
        db.session.add(new_user)
        db.session.commit()
        login_user(user=new_user,remember=True)

    return redirect(auth_url)


#reauthorize
@auth.route('/authorize')
def authorize():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect("/home")


#TODO doesn't work, need to delete session cookie but session.clear() doesn't work
@auth.route('/logout')
def logout():
    logout_user()
    session.clear()
    
    return redirect('/loginbutton')
    

#Redirected when logout
@auth.route('/loginbutton',methods=['GET','POST'])
def loginbutton():
    if request.method == 'POST':
        return redirect('/')
    return render_template('loginbutton.html')


def get_top_X():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    #TODO make sure right inputs. Timeframe prolly gotta be converted
    #Here you'll request form to get number_artists timeframe, or you could
    #searched_playlist = request.form.get('playlist')
    number_artists = request.form.get('number_artists')
    timeframe = request.form.get('timeframe')
    top_artists = sp.current_user_top_artists(limit=number_artists, time_range=timeframe)
    followed_artists = sp.current_user_followed_artists()
    
    signed_in_user=sp.current_user()
    #TODO you gotta parse this to get the artist name. Matter of fact propbaly can delete the get artist id part
    for artist in top_artists:
        #TODO 
        artist_name = artist['name']
        artist_id = artist['aritst_id']
        queried_artist = Artist.query.filter_by(spotify_user_id=signed_in_user['id'],artist_id=artist_id).first()
        if not queried_artist:
            new_artist = User(user_id = signed_in_user['id'],artist_id=artist_id,artist=artist_name)
            db.session.add(new_artist)
    for artist in followed_artists:
        artist_name = artist['name']
        artist_id = artist['aritst_id']
        queried_artist = Artist.query.filter_by(spotify_user_id=signed_in_user['id'],artist_id=artist_id).first()
        if not queried_artist:
            new_artist = User(user_id = signed_in_user['id'],artist_id=artist_id,artist=artist_name)
            db.session.add(new_artist)
    db.session.commit()


@auth.route('/home',methods=['GET','POST'])
def get_all_tracks():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    if request.method == 'POST':
        number_artists= 50
        #TODO , time_range=timeframe
        #default 6 months
        top_artists = sp.current_user_top_artists()
        followed_artists = sp.current_user_followed_artists()
        signed_in_user= sp.current_user()
        user_id = signed_in_user['id']
        for artist in top_artists['items']:
            artist_id = artist['id']
            artist_name = artist['name']

            queried_artist = Artist.query.filter_by(user_id=signed_in_user['id'],artist_id=artist_id).first()
            if queried_artist:
                pass
            else:
                new_artist = Artist(artist_id=artist_id,artist=artist_name,user_id=user_id)
                db.session.add(new_artist)
        for artist in followed_artists['items']:
            artist_id = artist['id']
            artist_name = artist['name']
            queried_artist = Artist.query.filter_by(user_id=signed_in_user['id'],artist_id=artist_id).first()
            if queried_artist:
                pass
            else:
                new_artist = Artist(artist_id=artist_id,artist=artist_name,user_id=user_id)
                db.session.add(new_artist)
        db.session.commit()
    return render_template('home.html',user=current_user)    
#TODO https://developers.google.com/maps/documentation/javascript/examples/places-searchbox#maps_places_searchbox-javascript
#https://stackoverflow.com/questions/18181458/auto-delete-a-record-in-table-when-date-is-expired
def find_all_concerts():
    tm_client = ticketpy.ApiClient(apikey)
    artists = get_top_X()
    concert_list=[]
    for artist in artists:
        concert_list.append({artist:[]})
        #TODO user can input state
        #latlong and radius variables
        venues = tm_client.events.find(keyword=artist,classification_name='Music',state_code='IL, OH').one()
        for venue in venues:
            print(venue)
    
    
#Checks to see if token is valid and gets a new token if not
def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid

#creates auth token
def create_spotify_oauth():
    return SpotifyOAuth(
            client_id='4e3d2cc9dfe2450890181834312c968d',
            client_secret='973e2a8c81b24a49891e69de31f143b4',
            redirect_uri="http://127.0.0.1:5000/authorize",
            scope="user-top-read user-library-read")
apikey = 'bH98AS06cMd23p9lqXUHk8cXI8M2ir6M' 
secret = 'KjUOGWGTI9Gbjh1a'