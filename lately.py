# from flask import Flask
# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello, Worlsdlfj d!'

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         return do_the_login()
#     else:
#         return show_the_login_form()

import json
from flask import Flask, request, redirect, g, render_template
import requests
import base64
import urllib

# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response. 


app = Flask(__name__)

#  Client Keys
CLIENT_ID = "2f6971f1733b410390b5c6fbd09ef6bc"
CLIENT_SECRET = "aa659d1b960344089e917bb80fe334a6"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)


# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000
# REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
REDIRECT_URI = "http://127.0.0.1:5000/callback/q"
SCOPE = "user-read-recently-played"
# "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

@app.route("/")
def index():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key,urllib.parse.quote(val)) for key,val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    print (auth_url)
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']

    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    base64encoded = base64.b64encode(("{}:{}".format(CLIENT_ID, CLIENT_SECRET)).encode())
    headers = {"Authorization": "Basic MmY2OTcxZjE3MzNiNDEwMzkwYjVjNmZiZDA5ZWY2YmM6YWE2NTlkMWI5NjAzNDQwODllOTE3YmI4MGZlMzM0YTY"}
    # print (headers)
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)
    # print(code_payload)
    # print(post_request.text)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    # print("RESPONSE DATA BELOW")
    print (response_data)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    print(refresh_token)
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]
    print(expires_in)

    # # Auth Step 6: Use the access token to access Spotify API

    endpoint_header = {"Authorization": "Bearer "+access_token}

    # # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=endpoint_header)
    profile_data = json.loads(profile_response.text)

    print("THIS IS PROFILE DATA ")
    print(profile_data)

    # # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=endpoint_header)
    playlist_data = json.loads(playlists_response.text)
    
    # # Combine profile and playlist data to display
    display_arr = [profile_data] + playlist_data["items"]
    return render_template("index.html",sorted_array=display_arr)

    
    # display_arr = [profile_data] + playlist_data["items"]
    # return base64encoded #auth_token #json.dumps(response_data)
    # return render_template("index.html") 
    # ,sorted_array=display_arr)


if __name__ == "__main__":
    app.run(debug=True,port=PORT)