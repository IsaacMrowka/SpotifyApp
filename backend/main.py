from flask import Flask, redirect, request, jsonify, session
import requests, os, datetime, urllib.parse
from datetime import datetime, timedelta
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from db_operations import Track, engine

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
    scope = 'user-read-private, user-read-email, user-library-read'
    params = {
        'client_id': os.getenv("CLIENT_ID"),
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': os.getenv("REDIRECT_URI"),
        'show_dialog': False,  # True renewed forces relogin for debugging
    }
    
    auth_url = f"{os.getenv('AUTH_URL')}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

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

        return redirect('http://localhost:5000/api/tracks')

def tokencheck():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('refresh-token')


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
    '''
    #endpoint to get genre through artist as it is not available through song data
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }        
    artist_response = requests.get(os.getenv("API_BASE_URL") + '/artists?ids=2CIMQHirSU0MQqyYHq0eOx%2C57dN52uHvrHOxijzpIgu3E%2C1vCWHaC5f2uS3yhpwWbIA6', headers=headers)
    '''
    #collect artist id's and then use new endpoint to access artrist genre data then add and commit to database connecting the song artist ids
    try:
        track_json = response.json()
        for item in track_json["items"]:
            track = item["track"]
            track_id = track["id"]
            track_name = track["name"]
            track_artist = track["artists"][0]
            artist_name = track_artist["name"]
            existing_track = DBsession.query(Track).filter(Track.id == track_id).first()
            if existing_track:
                existing_track.name = track_name
                existing_track.artist_name = artist_name
            else:
                new_track = Track(id=track_id, name=track_name, artist=artist_name)
                DBsession.add(new_track)
            
            DBsession.commit()
    except Exception as e:
        DBsession.rollback()
        return {"error": str(e)}, 500
    finally:
        DBsession.close()
    return track_json  

@app.route('/api/updatePlaylists')
def update_playlists():
    get_liked_tracks()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)