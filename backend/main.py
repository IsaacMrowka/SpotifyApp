from flask import Flask, redirect, request, jsonify, session
import requests, os, datetime, urllib.parse, json
from datetime import datetime, timedelta
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker, load_only
from sqlalchemy import asc, inspect
from db_operations import Track, Recommendations, NewPlaylist, engine

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"] ,supports_credentials=True)
app.secret_key = os.urandom(24)
load_dotenv()
Session = sessionmaker(bind=engine)
DBsession = Session()

@app.route('/')
def index():
    return "Welceom <a href='/login'>Login  spoofu </a>"

@app.route('/refresh-token')
def refresh_access_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': os.getenv("CLIENT_ID"),
            'client_secret': os.getenv("CLIENT_SECRET")
        }
        
    response = requests.post(os.getenv("TOKEN_URL"), data=req_body)

    if response.status_code == 200:
        new_token_info = response.json()
        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']
        
        return redirect('/playlists')

        
@app.route('/login')
def login():
    scope = 'user-read-private, user-read-email, user-library-read, playlist-read-private, playlist-read-collaborative, playlist-modify-public, playlist-modify-private'
    params = {
        'client_id': os.getenv("CLIENT_ID"),
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': os.getenv("REDIRECT_URI"),
        'show_dialog': False,  # True renewed forces relogin for debugging
    }
    
    auth_url = f"{os.getenv('AUTH_URL')}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url) #do not change url

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': os.getenv("REDIRECT_URI"),
            'client_id': os.getenv("CLIENT_ID"),
            'client_secret': os.getenv("CLIENT_SECRET")
        }

        response = requests.post(os.getenv("TOKEN_URL"), data=req_body)
        
        if response.status_code != 200:
            return jsonify({"error": "Failed to get access token"}), response.status_code
        
        token_info = response.json()
        
        session['access_token'] = token_info.get('access_token')
        session['refresh_token'] = token_info.get('refresh_token')
        session['expires_at'] = datetime.now().timestamp() + token_info.get('expires_in', 3600)

        return redirect('/api/create-playlist')

def tokencheck():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('refresh-token')

##--FUNCTIONS UNDERNEATH--##

@app.route('/api/playlists')
def get_playlists():
    tokencheck()
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    } 
    response = requests.get(os.getenv("API_BASE_URL") + 'me/playlists', headers=headers)
    return(response.json())

@app.route('/api/user')
def get_spotify_user():
    tokencheck()
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    response = requests.get(os.getenv("API_BASE_URL") + 'me', headers=headers)
    return response.json()

@app.route('/api/tracks')
def get_liked_tracks():
    tokencheck()

    #endpoint to get users liked songs
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }        
    response = requests.get(os.getenv("API_BASE_URL") + 'me/tracks?limit=10', headers=headers)
   
    try:
        track_json = response.json()
        for item in track_json["items"]:
            track = item["track"]
            track_id = track["id"]
            track_name = track["name"]
            existing_track = DBsession.query(Track).filter(Track.id == track_id).first()
            if existing_track:
                existing_track.name = track_name
            else:
                liked_tracks = Track(id=track_id, name=track_name)
                DBsession.add(liked_tracks)
            
            DBsession.commit()
    except Exception as e:
        DBsession.rollback()
        return {"error in database for liked": str(e)}, 500
    finally:
        DBsession.close()
    return response.json()

@app.route('/api/refresh')
def refresh_database():
    DBsession.query(NewPlaylist).delete()
    DBsession.commit()
    return redirect('/api/recommendations')

@app.route('/api/recommendations')
def get_recommendations():
    tokencheck()
    #endpoint to get track recommendations songs
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    try:
        response = requests.get(os.getenv("API_BASE_URL")+'recommendations?limit=100&seed_tracks=5plW0IS6XNNFFvLCH15edI', headers=headers)
        recommendations_json = response.json()
    except:
        if response.status_code == 200:
            try:
                data = response.json()
                print(data)
            except ValueError as e:
                print("JSON decode error:", e)
        elif response.status_code == 429:
            retry_after = response.headers.get('Retry-After')
            print("Too Many Requests: Retry after", retry_after, "seconds.")
        elif response.status_code == 401:
            print("Unauthorized: Check your access token.")
        elif response.status_code == 400:
            print("Bad Request: Check your query parameters.")
        else:
            print("Error:", response.status_code)
            print("Response content:", response.text)
    #delete any recommendations from prior request
    DBsession.query(Recommendations).delete()
    DBsession.commit()
    i = 1
    try:
        for track in recommendations_json["tracks"]:
            track_id = track["id"]
            track_name = track["name"]
            existing_track = DBsession.query(Track).filter(Recommendations.id == track_id).first()
            if existing_track:
                existing_track.name = track_name
            else:
                track_recommendations = Recommendations(index= i, id=track_id, name=track_name)
                DBsession.add(track_recommendations)
                i += 1

            DBsession.commit()
    except Exception as e:
        DBsession.rollback()
        return {"error in databse in recommendations": str(e)}, 500
    finally:
        DBsession.close()
    return redirect('/api/check-liked')  
#this database matches spotify response json

@app.route('/api/check-liked')
def get_liked_recommendations():
    tokencheck()
    headers = {
    'Authorization': f"Bearer {session['access_token']}"
    }
    minimum = DBsession.query(NewPlaylist).count()
    while minimum < 10:
        print (minimum)
        recommendations_id = DBsession.query(Recommendations.id).order_by(asc(Recommendations.index)).limit(100).all()
        recommendations_name = DBsession.query(Recommendations.name).order_by(asc(Recommendations.index)).limit(100).all()
        track_id_list = [str(recommendation.id) for recommendation in recommendations_id]
        track_id_join = ','.join(track_id_list)
        
        response = requests.get(os.getenv("API_BASE_URL") + 'me/tracks/contains?ids='+track_id_join, headers=headers)
        liked_recommendations_json = response.json()
        #index the 'true' bool from the json data
        liked_rec_string = json.dumps(liked_recommendations_json)
        split_string = liked_rec_string.split()
        index=[]
        for i, string in enumerate(split_string):
            if 'true' in string:
                index.append(i + 1)
        if index == []:
            print("No liked songs in recommendations pull")
    
        #find the corresponding indeces in the recommendations data
        new_id_list = []
        new_name_list = [str(recommendation.name) for recommendation in recommendations_name]
        for j, track in enumerate(track_id_list):
            if j in index and j<50:
                new_id_list.append(track_id_list[j-1])
                print(track_id_list[j-1])
                existing_track = DBsession.query(NewPlaylist).filter(NewPlaylist.id == track_id_list[j-1]).first()
                if existing_track:
                    existing_track.name = new_name_list[j-1]
                else:
                    new_tracks = NewPlaylist(id=track_id_list[j-1], name=new_name_list[j-1])
                    DBsession.add(new_tracks)
            DBsession.commit()
        return redirect('/api/recommendations')
    return redirect('/api/create-playlist')

@app.route('/api/create-playlist')
def create_playlist():
    tokencheck()
    headers = {
    'Authorization': f"Bearer {session['access_token']}"
    }
    #get user for creating playlist
    user_response = requests.get(os.getenv("API_BASE_URL") + 'me', headers=headers)
    user_json = user_response.json()
    user_id = None
    user_id = user_json.get('id')

    #get the playlist id after creation
    create_playlist_body = '{ "name": "TEST", "description": "Playlist based on recommendations", "public": false }'
    create_playlist_response = requests.post(os.getenv("API_BASE_URL") + 'users/'+user_id+'/playlists', data=create_playlist_body, headers=headers)
    create_playlist_json = create_playlist_response.json()
    playlist_id = create_playlist_json.get('id')

    #get tracks from databse
    new_tracks_id = DBsession.query(NewPlaylist.id).limit(1).all()
    track_id_list = [str(track.id) for track in new_tracks_id]
    track_id_list.insert(0,'')

    track_id_join = ', spotify:track:'.join(track_id_list)
    track_id_join.strip(', ')
    print (track_id_join, "OHOHOHOHOHOHOHOHOHOHOHOHOHOHOH")

    #testing WORKS
    test_id =['spotify:track:5plW0IS6XNNFFvLCH15edI', 'spotify:track:3GXSywNvYLAVUCtjMHkKDh']
    #add tracks to playlist
    # cant use tuple 
    #try to use track_id_list as a list
    #maybe split

    add_tracks_body = json.dumps({ "uris": test_id })
    response = requests.post(os.getenv("API_BASE_URL") + 'playlists/'+playlist_id+'/tracks', data=add_tracks_body, headers=headers)
    return(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)