import keys
import pandas as pd
import numpy as np
import requests
import streamlit as st


# This app is using Best Buy's API and RAWG Video Games Database API

# Title for this app
st.set_page_config(layout="wide", page_icon=":video_game:", page_title="Video Game App")

blank, title_col, blank = st.columns([2,3.5,2])


# Side Bar
add_selectbox = st.sidebar.selectbox(
  "Select:",
  ["Homepage", "Ratings", "Locations", "Feedback","Contact Info"]
)


if add_selectbox == "Homepage":
  title_col.title("Video Game App :video_game:")

# Search name for game
  game_to_search_for = st.text_input('Enter the name of the game you would like to search for:')

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
  #st.write(games_dict) # TODO: remove this line after fixing null search error

  games_list = []
  currGameGenres = ""

  # TODO: Fix error with j not defined when searching for certain names ("Grand", "Left", etc.) that do have games
  for i in games_dict["results"]:
      for j in i["genres"]:
              if(len(currGameGenres) == 0):
                  currGameGenres += j["name"]
      else:
          currGameGenres += ", " + j["name"]
          games_list.append([i["name"], currGameGenres, i["rating"], i["id"]])
          currGameGenres = ""

  if games_list:
      games_df = pd.DataFrame(
          games_list,
          columns=('Game', 'Genre', 'Rating', 'Unique ID'))
      st.dataframe(games_df)
      selected_games = st.selectbox('Select game:', games_df.index)

  else:
      st.error("No games found with the name" + game_to_search_for + ".")


# testing for Valrie




elif add_selectbox == "Ratings":
  # Add the chart with the ratings here
  title_col.title("Ratings :bar_chart:")
  st.write("To be constructed")


elif add_selectbox == "Locations":
  title_col.title("Locations :pushpin:")
  st.write("To be constructed")

  # Add the map here


elif add_selectbox == "Feedback":
  title_col.title("Feedback :memo:")

  username = st.text_input('Username')
  feedback = st.text_area('Feedback')

  if st.button('Enter'):
   if (len(feedback.strip())):
       st.info ("Feedback Saved")
   elif feedback:
        st.error("The feedback is empty")


  if username.isdigit():
      st.error("Username must contain both letters & numbers.")

  elif username.isalpha():
      st.error("Username must contain both letters & numbers.")

  elif username:
      st.success("Username Accepted")


elif add_selectbox == "Contact Info":
  title_col.title("Contact Info :telephone_receiver:")
  st.write("Further Assitance: [Get Help](https://www.bestbuy.com/site/electronics/customer-service/pcmcat87800050001.c?id=pcmcat87800050001&ref=212&loc=1&gclid=CjwKCAjwi6WSBhA-EiwA6Niokw2dEMikiJxDWkWZtjXiKCwS6qF1sTLZzMt-c9n7VaKOzXMFJbWT0xoCHtYQAvD_BwE&gclsrc=aw.ds)")