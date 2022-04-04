import keys
import streamlit as st
import pandas as pd
import numpy as np
import requests

# This app is using Best Buy's API and RAWG Video Games Database API

# Title for this app
st.title("Video Game App")

# Search name for game
game_to_search_for = "Super Mario"
currPage = 1

# Used to replace spaces in a search with +'s, so that the URL actually works
def fixForURL(string):
    string = string.replace(" ", "+")
    return string

# The URL used for searching by game name
# TODO: The URL here should be using Best Buy's API, not RAWG. The RAWG API should be used solely for metadata like ratings, genre, etc.
games_url = "https://api.rawg.io/api/games?key=" + keys.RAWG_API_KEY + "&search=" + fixForURL(game_to_search_for) + "&page=" + str(currPage)
print("The URL of the API request:" + games_url)

# Creates a dictionary (like an array but the indexes are "keys" (strings) rather than integers) using info returned from the URL request
games_dict = requests.get(games_url).json()

games_list = []
currGameGenres = ""

for i in games_dict["results"]:
    for j in i["genres"]:
        if(len(currGameGenres) == 0):
            currGameGenres += j["name"]
        else:
            currGameGenres += ", " + j["name"]
    games_list.append([i["name"], currGameGenres, i["rating"], i["id"]])
    currGameGenres = ""

games_df = pd.DataFrame(
    games_list,
    columns=('Game', 'Genre', 'Rating', 'Unique ID'))

st.dataframe(games_df)

selected_games = st.selectbox('Select game:', games_df.index)