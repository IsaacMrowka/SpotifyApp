from flask import Flask, redirect, request, jsonify, session
import requests, os, datetime, urllib.parse
from datetime import datetime, timedelta
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker, load_only
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
    scope = 'user-read-private, user-read-email, user-library-read'
    params = {
        'client_id': os.getenv("CLIENT_ID"),
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': os.getenv("REDIRECT_URI"),
        'show_dialog': True,  # True renewed forces relogin for debugging
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

        return redirect('/api/tracks')

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
    return redirect('/api/recommendations')  

@app.route('/api/recommendations')
def get_recommendations():
    tokencheck()
    #endpoint to get track recommendations songs
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    DBtrack = DBsession.query(Track).options(load_only(Track.id)).first()
    track_id = DBtrack.id
    response = requests.get(os.getenv("API_BASE_URL") + 'recommendations?limit=50&seed_tracks=0WQZG47PGOUzuQuMpB8gC0', headers=headers)
    recommendations_json = response.json()
    try:
        for track in recommendations_json["tracks"]:
            track_id = track["id"]
            track_name = track["name"]
            existing_track = DBsession.query(Track).filter(Recommendations.id == track_id).first()
            if existing_track:
                existing_track.name = track_name
            else:
                track_recommendations = Recommendations(id=track_id, name=track_name)
                DBsession.add(track_recommendations)

            DBsession.commit()
    except Exception as e:
        DBsession.rollback()
        return {"error in databse in recommendations": str(e)}, 500
    finally:
        DBsession.close()
    return redirect('/api/check-liked')  

@app.route('/api/check-liked')
def check_liked():
    tokencheck()
    headers = {
    'Authorization': f"Bearer {session['access_token']}"
    }    
    recommendations = DBsession.query(Recommendations.id, Recommendations.name).all()
    liked_recommendations_json = []

    for recommendation in recommendations:
        track_id = recommendation.id
        track_name = recommendation.name

        response = requests.get(os.getenv("API_BASE_URL") + 'me/tracks/contains?ids='+track_id, headers=headers)
        liked_recommendations_json.append(response.json())
        #from Recommendations move to new table Generated playlist
        for check in liked_recommendations_json:
            if check == 'true':
                existing_track = DBsession.query(NewPlaylist).filter(NewPlaylist.id == track_id).first()
                if existing_track:
                    existing_track.name = track_name
            else:
                track_recommendations = NewPlaylist(id=track_id, name=track_name)
                DBsession.add(track_recommendations)
    DBsession.close()
    return liked_recommendations_json

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)