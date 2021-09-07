from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

URL = "https://www.billboard.com/charts/hot-100/"
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URL = "http://127.0.0.1:9090"
SCOPE = "playlist-modify-private"

time = input("What year would you like to travel to? Enter in YYYY-MM-DD: ")

response = requests.get(f"{URL}{time}")
data = response.text

soup = BeautifulSoup(data, "html.parser")
song_tag = soup.find_all(name="span", class_="chart-element__information__song text--truncate color--primary")
songs = []
for song in song_tag:
    songs.append(song.getText())

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URL,
                                               scope=SCOPE,
                                               show_dialog=True,
                                               cache_path="token.txt"
                                               ))

user_id = sp.current_user()["id"]
song_uris = []


def search_songs():
    for track in songs:
        try:
            year = time.split("-")[0]
            results = sp.search(q=f"track:{track} year:{year}", limit=1, type="track")
            track_uri = results['tracks']['items'][0]['id']
            full_uri = f"spotify:track:{track_uri}"
            song_uris.append(full_uri)
        except IndexError:
            print(f"Song: {track} not found.")


def create_playlist():
    playlist = sp.user_playlist_create(user=user_id,
                                       name=f"{time} Billboard 100",
                                       public=False,
                                       description=f"Top 100 as of {time}, created in python by Aditya Nair")

    playlist_id = playlist["id"]
    add_tracks = sp.playlist_add_items(playlist_id=playlist_id, items=song_uris)
    print(add_tracks)

search_songs()
create_playlist()
