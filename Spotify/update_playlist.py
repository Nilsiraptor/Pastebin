import json

import requests as rq


CLIENT_ID = ""
CLIENT_SECRET = ""


# --- Load Access Tokens
with open("token.json", "r") as file:
    obj = json.load(file)

ACCESS_TOKEN = obj["access_token"]
REFRESH_TOKEN = obj["refresh_token"]
PLAYLIST_ID = obj["playlist_id"]
TOP = obj.get("top", "50")
TIME_RANGE = obj.get("time_range", "short_term")
print("Finished loading tokens and settings")


# --- Refresh Access Token
body = {
    "grant_type": "refresh_token",
    "refresh_token": REFRESH_TOKEN
}
header = {
    "Content-Type": "application/x-www-form-urlencoded"
}
response = rq.post(url=f"https://accounts.spotify.com/api/token", data=body, headers=header, auth=(CLIENT_ID, CLIENT_SECRET))

if response.status_code == 200:
    data = response.json()

    ACCESS_TOKEN = data["access_token"]
    REFRESH_TOKEN = data.get("refresh_token", REFRESH_TOKEN)

    with open("token.json", "w") as file:
        json.dump({"access_token": ACCESS_TOKEN,
                   "refresh_token": REFRESH_TOKEN},
                   file, indent=4)
else:
    raise Exception(response.text)
print("Finished refreshing access token")


# --- Get Top Songs
url = f"https://api.spotify.com/v1/me/top/tracks"

if TOP == "100":
    offsets = ["0", "50"]
else:
    offsets = ["0"]

song_uri = []

for off in offsets:
    body = {
        "time_range": TIME_RANGE,
        "limit": "50",
        "offset": off
    }

    header = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    r = rq.get(url, params=body, headers=header)
    if r.status_code != 200:
        raise Exception(r.text)

    songs = r.json()["items"]
    song_uri += [song["uri"] for song in songs]
print("Finished retrieving user's top songs")


# --- Update Songs in Playlist
url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks"

body = {
    "uris": song_uri
}

header = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

r = rq.put(url, json=body, headers=header)
if r.status_code != 200:
    raise Exception(r.text)
print("Finished updating playlist with top songs")


# --- Save new IDs
with open("token.json", "w") as file:
    json.dump({"access_token": ACCESS_TOKEN,
               "refresh_token": REFRESH_TOKEN,
               "playlist_id": PLAYLIST_ID,
               "top": TOP,
               "time_range": TIME_RANGE},
               file, indent=4)

print("Finished saving new tokens and settings")
