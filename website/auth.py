import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, url_for, session, request, redirect, flash,render_template,Blueprint,make_response
import json
import time
import pandas as pd
from flask_login import login_user, logout_user, current_user
from . import db
from . models import User,Artist,Concert
import ticketpy
import geocoder



#ddd
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


#TODO its the cookies that keep it up. if you click the info bar top left of the browser you can see them and manually remove them, then when you click logout that shit will put
#you in the right place. The code below does not delete nor set the cookies to expire, so gotta figure that out. At least i know what the problem is now
@auth.route('/logout')
def logout():
    logout_user()
    session.clear()
    response = make_response("Cookie Cleared")
    response.delete_cookie("spotify-login-session")
    response.delete_cookie('remember_token')
    response.delete_cookie('http://127.0.0.1:5000')
    #response.delete_cookie('sp_dc')
    #response.delete_cookie('sp_key')
    response.set_cookie('sp_dc','',expires=0)
    response.set_cookie('sp_key','',expires=0)

    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)
    




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
    #rtists = sp.current_user_rtists()
    
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
    s="""for artist in rtists:
        artist_name = artist['name']
        artist_id = artist['aritst_id']
        queried_artist = Artist.query.filter_by(spotify_user_id=signed_in_user['id'],artist_id=artist_id).first()
        if not queried_artist:
            new_artist = User(user_id = signed_in_user['id'],artist_id=artist_id,artist=artist_name)
            db.session.add(new_artist)"""
    db.session.commit()

@auth.route('/concerts',methods=['GET'])
def concerts():
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    signed_in_user= sp.current_user()
    user_id = signed_in_user['id']
    queried_concerts = Concert.query.filter_by(user_id=user_id).first()
    return render_template('concerts.html',user=current_user)


@auth.route('/home',methods=['GET','POST'])
def get_all_tracks():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
#TODO need to use geolocation api to get the user actual location, the one below don't really count
    
    if request.method == 'POST':
        g = geocoder.ip('me')
        latland = g.latlng
        longitude = request.form.get('longitude')
        latitude = request.form.get('latitude')
        #isnt getting the radius
        radius = request.form.get('radius')
        number_artists = request.form.get('number_artists')
   
        #TODO , time_range=timeframe
        #default 6 months
        top_artists = sp.current_user_top_artists(limit=number_artists)
        signed_in_user= sp.current_user()
        user_id = signed_in_user['id']
        tm_client = ticketpy.ApiClient(apikey)

        for artist in top_artists['items']:
            artist_id = artist['id']
            artist_name = artist['name']
            queried_artist = Artist.query.filter_by(user_id=signed_in_user['id'],artist_id=artist_id,artist=artist_name).first()
            if not queried_artist:
                new_artist = Artist(artist_id=artist_id,artist=artist_name,user_id=user_id)
                db.session.add(new_artist)
            
            concerts_list = []
            time.sleep(1)
            #TODO put actual latlong in, also have user input radius. Have my vpn on so yknow
             
            #venues = tm_client.events.find(keyword="Sidney Gish",classification_name='Music',radius=100,sort='relevance,asc',latlong=[41.8,-87.6],unit='miles').one()
            concerts = tm_client.events.find(keyword=artist_name,classification_name='Music',radius=radius,latlong=[latitude,longitude],unit='miles')
            #concerts = tm_client.events.find(keyword=artist,classification_name='Music',state_code='IL, OH').one()

            #TODO need a mechanism to determine if its an actual concert by that person or not. You'll get a lot of bullshit, like 90s weeknd for the weeknd
            
            for concert in concerts:
                #TODO all these concerts are empty
                if concert:
                    concert_json = concert.json
                    concert_json = concert_json['_embedded']['events'][0]
                    concert_id = concert_json['id']
                    #TODO the problem is that some of the json's returned from the queried_concert have totally different strucutre. See test and test2. Shit annoying ash 
                    try:
                        queried_concert = Concert.query.filter_by(user_id=signed_in_user['id'],concert_id=concert_id).first()
                    #TODO sussy except block
                    except KeyError:
                        queried_concert = 'error prolly lmao'
                    if not queried_concert:
                        concert_json = concert.json
                        concert_json = concert_json['_embedded']['events'][0]
                        concert_id = concert_json['id']
                        try:
                            concert_url = concert_json['url']
                        except KeyError:
                            concert_url=None
                        try:
                            concert_name = concert_json['name']
                        except KeyError:
                            concert_name=None
                        try:
                            concert_image = concert_json['images'][0]['url']
                        except KeyError:
                            concert_image=None
                        try:
                            concert_distance = concert_json['distance']
                        except KeyError:
                            concert_distance=None
                        try:
                            concert_date = concert_json['dates']['start']['dateTime']
                        except KeyError:
                            concert_date=None
                        try:
                            concert_min_price = concert_json['priceRanges'][0]['min']
                        except KeyError:
                            concert_min_price=None
                        try:
                            concert_max_price = concert_json['priceRanges'][0]['max']
                        except KeyError:
                            concert_date=None
                        try:
                            concert_venue_name = concert_json['_embedded']['venues'][0]['name']
                        except KeyError:
                            concert_venue_name=None
                        try:
                            concert_city = concert_json['_embedded']['venues'][0]['city'].get('name')
                        except KeyError:
                            concert_city=None

                        new_concert = Concert(user_id=signed_in_user['id'],concert_artist = artist_id,city=concert_city,date=concert_date,max_price=concert_max_price,min_price=concert_min_price,venue=concert_venue_name,dist=concert_distance,concert_image=concert_image,concert_name=concert_name,concert_id=concert_id)     
                        db.session.add(new_concert)

        db.session.commit()
        return render_template('concerts.html',user=current_user)
    return render_template('home.html',user=current_user)    
#TODO https://developers.google.com/maps/documentation/javascript/examples/places-searchbox#maps_places_searchbox-javascript
#https://stackoverflow.com/questions/18181458/auto-delete-a-record-in-table-when-date-is-expired
def find_all_concerts():
    tm_client = ticketpy.ApiClient(apikey)
    artists = get_top_X()
    concert_list={}
    for artist in artists:
        
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
            client_id='',
            client_secret='',
            redirect_uri="http://127.0.0.1:5000/authorize",
            scope="user-top-read user-library-read")
apikey = '' 
secret = ''