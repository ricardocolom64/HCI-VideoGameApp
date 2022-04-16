import requests
import streamlit as st
import pandas as pd
import keys
import pandas as pd

def fixForURL(string):
    string = string.replace(" ", "")
    return string

#copied and modified Jada's code into a function
def ratings_data(game_to_search_for):
    # Used to replace spaces in a search with +'s, so that the URL actually works

    games_url = "https://api.rawg.io/api/games?key=" + keys.RAWG_API_KEY + "&search=" + fixForURL(
        game_to_search_for)
    print("The URL of the API request:" + games_url)

    # Creates a dictionary (like an array but the indexes are "keys" (strings) rather than integers) using info returned from the URL request
    games_dict = requests.get(games_url).json()
    game_options = games_dict["results"]

    select_game_options = []
    for i in range(len(game_options)):
        select_game_options.append(str(i) + " - " + str(game_options[i]["name"]))

    selected_game = st.selectbox('Select game:', select_game_options)

    if selected_game:
        game_to_search_for = selected_game
        games_url = "https://api.rawg.io/api/games?key=" + keys.RAWG_API_KEY + "&search=" + fixForURL(
            game_to_search_for)
        print("The URL of the API request:" + games_url)

        games_dict = requests.get(games_url).json()

        ratings_list = [0, 0, 0, 0, 0, 0]
        reviewers = 0
        for i in games_dict["results"][0]["ratings"]:
            rating_score = i["id"]
            rating_count = i["count"]
            reviewers += rating_count
            ratings_list[rating_score] = rating_count

        for i in range(len(ratings_list)):
            ratings_list[i] = ratings_list[i]/reviewers

        return ratings_list

def compare_game(game1, game2):

    game1_ratings = ratings_data(game1)
    game2_ratings = ratings_data(game2)

    df = pd.DataFrame(list(zip(game1_ratings, game2_ratings)),
                      columns=[str(game1).capitalize(), str(game2).capitalize()])

    st.line_chart(df)

