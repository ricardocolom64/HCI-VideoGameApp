import requests
import streamlit as st
import pandas as pd
import keys
import plotly.figure_factory as ff

def fixForURL(string):
    string = string.replace(" ", "+")
    return string

#copied jada's code into a function for easier retrieval for the histogram
def ratings(game_to_search_for):
    # Used to replace spaces in a search with +'s, so that the URL actually works

    games_url = "https://api.rawg.io/api/games?key=" + keys.RAWG_API_KEY + "&search=" + fixForURL(
        game_to_search_for)
    print("The URL of the API request:" + games_url)

    # Creates a dictionary (like an array but the indexes are "keys" (strings) rather than integers) using info returned from the URL request
    games_dict = requests.get(games_url).json()
    game_options = games_dict["results"]

    select_game_options = [""]
    for i in range(len(game_options)):
        select_game_options.append(str(i) + " - " + str(game_options[i]["name"]))

    selected_game = st.selectbox('Select game:', select_game_options)

    if selected_game:
        game_to_search_for = selected_game
        games_url = "https://api.rawg.io/api/games?key=" + keys.RAWG_API_KEY + "&search=" + fixForURL(
            game_to_search_for)
        print("The URL of the API request:" + games_url)

        # Creates a dictionary (like an array but the indexes are "keys" (strings) rather than integers) using info returned from the URL request
        games_dict = requests.get(games_url).json()

        ratings_dict = {0: [], 1: [], 2: [], 3: [], 4: [], 5: []}

        for i in games_dict["results"][0]["ratings"]:
            rating_score = i["id"]
            rating_count = i["count"]
            ratings_dict[rating_score].append(rating_count)

        ratings_list = []
        for j in range(6):
            if (ratings_dict[j].__len__() == 0):
                ratings_dict[j].append(0)
            ratings_list.append(ratings_dict[j])

        return ratings_list

def compare_game(game1, game2):
    game1_ratings = ratings(game1)
    game2_ratings = ratings(game2)

    hist_data = [game1_ratings, game2_ratings]
    group_labels = [game1, game2]

    fig = ff.create_distplot(
        hist_data, group_labels, bin_size=[0, 1, 2, 3, 4, 5]
    )
    st.plotly_chart(fig, use_container_width=True)

compare_game("Portal 2", "Reciever 2")
