import sys
import json
import urllib.parse as up

import requests as rq
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl


CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URI = "https://localhost"


# Create URL for user sign in
scopes = [
    "user-read-playback-state",
    "user-read-currently-playing",
    "playlist-read-private",
    "playlist-read-collaborative",
    "playlist-modify-private",
    "playlist-modify-public",
    "user-top-read",
    "user-read-recently-played",
    "user-read-private"
]

data = {
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "state": "0",
    "scope": " ".join(scopes)
}

url = f"https://accounts.spotify.com/authorize?{up.urlencode(data)}"


# Start web browser for user sign in
app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("Top Songs Playlist Updater")
window.setGeometry((1920-550)//2, 50, 550, 900)

browser = QWebEngineView()
window.setCentralWidget(browser)

class WebEnginePage(QWebEnginePage):
    """Custom QWebEnginePage to capture URL directs."""

    def acceptNavigationRequest(self, url: QUrl, type: 'QWebEnginePage.NavigationType', isMainFrame: bool) -> bool:
        """
        This method is called when a navigation request is made.
        You can inspect the type of navigation here.
        For example, QWebEnginePage.NavigationType.NavigationTypeRedirect
        indicates a redirect.
        """
        if type == QWebEnginePage.NavigationType.NavigationTypeRedirect:
            if url.toString().startswith(REDIRECT_URI):
                global redirect_url
                redirect_url = url.toString()
                window.close()
        return super().acceptNavigationRequest(url, type, isMainFrame)


home_page = WebEnginePage(browser)
browser.setPage(home_page)

browser.setUrl(QUrl(url))

window.show()

app.exec()


# Extract Authorization Code from redirect uri
parsed_url = up.urlparse(redirect_url)
data = up.parse_qs(parsed_url.query)

if "error" in data.keys():
    exit()

AUTHORIZATION_CODE = data["code"][0]


# Get Access Token and Refresh Token from Spotify API
data = {
    "grant_type": "authorization_code",
    "code": AUTHORIZATION_CODE,
    "redirect_uri": REDIRECT_URI
}

r = rq.post(url="https://accounts.spotify.com/api/token",
            data=data,
            auth=(CLIENT_ID, CLIENT_SECRET))

if not r.status_code == 200:
    exit()

tokens = r.json()
ACCESS_TOKEN = tokens["access_token"]
REFRESH_TOKEN = tokens["refresh_token"]


# Save all tokens to token.json
with open("token.json", "w") as file:
    json.dump({"access_token": ACCESS_TOKEN,
               "refresh_token": REFRESH_TOKEN},
               file, indent=4)
