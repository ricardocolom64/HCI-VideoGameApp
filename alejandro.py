import requests
import streamlit as st
import pandas as pd
import keys
import pandas as pd

st.title("Compare Two Games")
game1 = st.text_input("Look for game one.")
game2 = st.text_input("Look for game two.")


# Replace spaces for - on purpose, that's how slug is defined in the api.
def fix_url_for_slug(string):
    new_string = string.replace(" ", "-").replace("'", "").lower()
    return new_string


# copied and modified Jada's code into a function
def ratings_data(game_to_search_for):
    game_to_search_for = fix_url_for_slug(game_to_search_for)
    games_url = "https://api.rawg.io/api/games?key=" + keys.RAWG_API_KEY + "&search=" + fix_url_for_slug(
        game_to_search_for)
    print("The URL of the API request:" + games_url)

    # Creates a dictionary (like an array but the indexes are "keys" (strings) rather than integers) using info returned from the URL request
    games_dict = requests.get(games_url).json()
    found_game = {}
    for i in games_dict["results"]:
        if i["slug"] in game_to_search_for or game_to_search_for in i["slug"]:
            found_game = i
            break
    if found_game:
        ratings_list = [0, 0, 0, 0, 0, 0]
        reviewers = 0
        for i in found_game["ratings"]:
            rating_score = i["id"]
            rating_count = i["count"]
            reviewers += rating_count
            ratings_list[rating_score] = rating_count
        if reviewers > 0:
            for i in range(len(ratings_list)):
                ratings_list[i] = ratings_list[i] / reviewers
        else:
            st.warning("No reviews found for " + found_game["name"])
        game_return = [found_game["name"], ratings_list]
        # [Name of the game, List of ratings] more things can be added
        return game_return
    else:
        st.error("Game not found. Please try spelling it a different way, or try a different game.")


def retail_data(game):
    best_buy_request = "https://api.bestbuy.com/v1/products(search={0})?format=json&show=sku,name,salePrice&apiKey={1}".format(
        str(game), keys.BESTBUY_API_KEY)

    retail_game_dict = requests.get(best_buy_request).json()
    return retail_game_dict


def compare_game(game1, game2):
    game1_ratings = ratings_data(game1)
    game2_ratings = ratings_data(game2)
    if isinstance(game1_ratings, list) and isinstance(game2_ratings, list) \
            and game1 and game2:
        df = pd.DataFrame(list(zip(game1_ratings[1], game2_ratings[1])),
                          columns=[game1_ratings[0], game2_ratings[0]])
        st.line_chart(df)
        game1_col, game2_col = st.columns(2)
        with game1_col:
            st.subheader("Information about " + game1_ratings[0])
        with game2_col:
            st.subheader("Information about " + game2_ratings[0])


compare_game(str(game1), str(game2))

