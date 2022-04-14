import math
import keys
import pandas as pd
import numpy as np
import requests
import streamlit as st
from streamlit_bokeh_events import streamlit_bokeh_events
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
import pydeck as pdk

# This app is using Best Buy's API and RAWG Video Games Database API

# Title for this app
st.set_page_config(layout="wide", page_icon=":video_game:", page_title="Video Game App")

blank, title_col, blank = st.columns([2, 3.5, 2])

# Side Bar
add_selectbox = st.sidebar.selectbox(
    "Select:",
    ["Homepage", "Ratings", "Locations", "Feedback", "Contact Info"]
)

# ------------- HOMEPAGE -------------
if add_selectbox == "Homepage":
    title_col.title("Video Game App :video_game:")

    if 'currPage' not in st.session_state:
        st.session_state['currPage'] = 1

    # Used to change pages when necessary
    def fixPage(page):
        if (page == "Prev"):
            if (st.session_state.currPage <= 2):
                st.session_state.currPage = 1
            else:
                st.session_state.currPage -= 1
        if (page == "Next"):
            st.session_state.currPage += 1
        if (page == "Reset"):
            st.session_state.currPage = 1
        if (page == "First"):
            st.session_state.currPage = 1
        if (page == "Last"):
            st.session_state.currPage = (math.ceil(games_dict["count"] / 20))

    # Search name for game
    game_to_search_for = st.text_input('Enter the name of the game you would like to search for:',
                                       on_change=fixPage, args=("Reset",))

    # Used to replace spaces in a search with +'s, so that the URL actually works
    def fixForURL(string):
        string = string.replace(" ", "+")
        return string

    games_list = []
    currGameGenres = ""

    # Creates a streamlit multiselect widget to select what types of info the user would like to include in the table
    selectTableInfo = st.multiselect(
        'What info would you like to show on this list of games?',
        ['Genre', 'Rating', 'Release Date']
    )

    # If 'Genre' is selected on the above multiselect...
    # Creates a streamlit selectbox widget to select what genre the user would like to filter by
    if ('Genre' in selectTableInfo):
        selectGenre = st.selectbox(
            'What Genre would you like to search for?',
            ('All', 'Action', 'Adventure', 'Arcade', 'Board Games', 'Card', 'Casual', 'Educational', 'Family', 'Fighting',
             'Indie', 'Massively Multiplayer', 'Platformer', 'Puzzle', 'Racing', 'RPG', 'Simulation', 'Shooter', 'Sports', 'Strategy'),
            on_change=fixPage, args=("Reset",)
        )
    # Otherwise, set the selectGenre variable to 'Null'
    else:
        selectGenre = 'Null'

    # add a query parameter for genres to the search, if requested by the user
    def doGenreSearch():
        if (selectGenre == 'All') | (selectGenre == 'Null'):
            return ""
        else:
            return "&genres=" + selectGenre.lower()

    # Creates a double-sided slider that lets the user provide a range of ratings to filter the results
    if ('Rating' in selectTableInfo):
        startRating, endRating = st.slider('Enter the range of Metacritic ratings',
                                           value=(0, 100),
                                           step=1,
                                           on_change=fixPage, args=("Reset",))

    # add a query parameter for ratings to the search, if requested by the user
    def doRatingsSearch():
        if ('Rating' in selectTableInfo):
            return "&metacritic=" + str(startRating) + "," + str(endRating)
        else:
            return ""

    # The URL used for searching by game name
    games_url = "https://api.rawg.io/api/games?key=" + keys.RAWG_API_KEY + "&search=" + fixForURL(
        game_to_search_for) + "&page=" + str(st.session_state.currPage) + doGenreSearch() + doRatingsSearch()
    print("The URL of the API request:" + games_url)

    # Creates a dictionary (like an array but the indexes are "keys" (strings) rather than integers) using info returned from the URL request
    games_dict = requests.get(games_url).json()

    # This chooses what info to include in our games_list array, which will be used to fill in the dataframe (table)
    for i in games_dict["results"]:

        # This fills in our currGameGenres string (a list of genres) for the specified game, seperated by ', '
        # (each game may have multiple genres)
        for j in i["genres"]:
            if (len(currGameGenres) == 0):
                currGameGenres += j["name"]
            else:
                currGameGenres += ", " + j["name"]

        # If a currGameGenres contains the genre selected by selectGenre,
        # or selectGenre is set to 'All' or 'Null', then display the respective data.
        if ('All' == selectGenre) | (selectGenre in currGameGenres) | ('Null' == selectGenre):
            # If selectTableInfo multiselect includes Genre, Release Date, and Ratings
            if ('Genre' in selectTableInfo) & ('Release Date' in selectTableInfo) & ('Rating' in selectTableInfo):
                # Adds game to results list if the rating is in the range provided by the user
                if (i["metacritic"] is None):
                    games_list.append(
                        [i["name"], currGameGenres, i["released"], i["metacritic"], i["ratings_count"], i["id"]])
                elif ((i["metacritic"] >= startRating) & (i["metacritic"] <= endRating)):
                    games_list.append(
                        [i["name"], currGameGenres, i["released"], i["metacritic"], i["ratings_count"], i["id"]])

            # If selectTableInfo multiselect includes Genre, Release Date
            elif ('Genre' in selectTableInfo) & ('Release Date' in selectTableInfo):
                games_list.append([i["name"], currGameGenres, i["released"], i["id"]])

            # If selectTableInfo multiselect includes Genre, Ratings
            elif ('Genre' in selectTableInfo) & ('Rating' in selectTableInfo):
                # Adds game to results list if the rating is in the range provided by the user
                if (i["metacritic"] is None):
                    games_list.append([i["name"], currGameGenres, i["metacritic"], i["ratings_count"], i["id"]])
                elif ((i["metacritic"] >= startRating) & (i["metacritic"] <= endRating)):
                    games_list.append([i["name"], currGameGenres, i["metacritic"], i["ratings_count"], i["id"]])


            # If selectTableInfo multiselect includes Release Date, and Ratings
            elif ('Release Date' in selectTableInfo) & ('Rating' in selectTableInfo):
                # Adds game to results list if the rating is in the range provided by the user
                if (i["metacritic"] is None):
                    games_list.append([i["name"], i["released"], i["metacritic"], i["ratings_count"], i["id"]])
                elif ((i["metacritic"] >= startRating) & (i["metacritic"] <= endRating)):
                    games_list.append([i["name"], i["released"], i["metacritic"], i["ratings_count"], i["id"]])

            # If selectTableInfo multiselect only includes Genre
            elif ('Genre' in selectTableInfo):
                games_list.append([i["name"], currGameGenres, i["id"]])

            # If selectTableInfo multiselect only includes Release Date
            elif ('Release Date' in selectTableInfo):
                games_list.append([i["name"], i["released"], i["id"]])

            # If selectTableInfo multiselect only includes Ratings
            elif ('Rating' in selectTableInfo):
                # Adds game to results list if the rating is in the range provided by the user
                if (i["metacritic"] is None):
                    games_list.append([i["name"], i["metacritic"], i["ratings_count"], i["id"]])
                elif ((i["metacritic"] >= startRating) & (i["metacritic"] <= endRating)):
                    games_list.append([i["name"], i["metacritic"], i["ratings_count"], i["id"]])

            # If selectTableInfo multiselect doesn't include any options
            else:
                games_list.append([i["name"], i["id"]])

        # empty out the currGameGenres string, to be filled out by the new game's genre data when the loop reiterates
        currGameGenres = ""

    if games_list:
        # If the data filled into games_list includes Genre, Release Date, and Ratings
        if ('Genre' in selectTableInfo) & ('Release Date' in selectTableInfo) & ('Rating' in selectTableInfo):
            games_df = pd.DataFrame(
                games_list,
                columns=('Game', 'Genre', 'Released', 'Rating', 'Number of Ratings', 'Unique ID'))

        # If the data filled into games_list includes Genre and Release Date
        elif ('Genre' in selectTableInfo) & ('Release Date' in selectTableInfo):
            games_df = pd.DataFrame(
                games_list,
                columns=('Game', 'Genre', 'Released', 'Unique ID'))

        # If the data filled into games_list includes Genre and Ratings
        elif ('Genre' in selectTableInfo) & ('Rating' in selectTableInfo):
            games_df = pd.DataFrame(
                games_list,
                columns=('Game', 'Genre', 'Rating', 'Number of Ratings', 'Unique ID'))

        # If the data filled into games_list includes Release Date and Ratings
        elif ('Release Date' in selectTableInfo) & ('Rating' in selectTableInfo):
            games_df = pd.DataFrame(
                games_list,
                columns=('Game', 'Release Date', 'Rating', 'Number of Ratings', 'Unique ID'))

        # If the data filled into games_list includes Genre
        elif ('Genre' in selectTableInfo):
            games_df = pd.DataFrame(
                games_list,
                columns=('Game', 'Genre', 'Unique ID'))

        # If the data filled into games_list includes Release Date
        elif ('Release Date' in selectTableInfo):
            games_df = pd.DataFrame(
                games_list,
                columns=('Game', 'Released', 'Unique ID'))

        # If the data filled into games_list includes Ratings
        elif ('Rating' in selectTableInfo):
            games_df = pd.DataFrame(
                games_list,
                columns=('Game', 'Rating', 'Number of Ratings', 'Unique ID'))

        # If the data filled into games_list does not include Genre, Release Date, or Ratings
        else:
            games_df = pd.DataFrame(
                games_list,
                columns=('Game', 'Unique ID'))

        st.dataframe(games_df)

    else:
        st.error("No games matched your request")


    # Used to write "[current page #] of [total # of pages]"
    def writePage():
        st.write("Page: " + str(st.session_state.currPage) + " of " + str(math.ceil(games_dict["count"] / 20)))


    # These columns are used to display the page info & buttons nicely along one row
    col1, col2, col3, col4, col5 = st.columns([0.6, 1, 1.2, 1, 5.1])

    # The following will correctly display the page buttons and the page #.
    # (prev page and next page buttons will not show if there is no previous page or next page, respectively)
    with col1:
        if (st.session_state.currPage != 1):
            if st.button("<<<", on_click=fixPage, args=("First",)):
                print("")
    with col2:
        if (st.session_state.currPage != 1):
            if st.button("Prev Page", on_click=fixPage, args=("Prev",)):
                print("")
    with col3:
        writePage()
    with col4:
        if (games_dict["next"] is not None):
            if st.button("Next Page", on_click=fixPage, args=("Next",)):
                print("")
    with col5:
        if (games_dict["next"] is not None):
            if st.button(">>>", on_click=fixPage, args=("Last",)):
                print("")

    if (games_list):
        select_game_options = ["..."]
        for i in range(len(games_df.index)):
            select_game_options.append(str(i) + " - " + str(games_list[i][0]))

        selected_game = st.selectbox('Select a game to learn more about:', select_game_options)
        selected_game_id = ""

        if (selected_game != "..."):
            selected_game_id = games_list[int(selected_game[0])][1]

            selected_game_url = "https://api.rawg.io/api/games/" + str(selected_game_id) + "?key=" + keys.RAWG_API_KEY

            # Creates a dictionary (like an array but the indexes are "keys" (strings) rather than integers) using info returned from the URL request
            selected_game_dict = requests.get(selected_game_url).json()

            game_desc = selected_game_dict["description"].replace('<p>', '').replace('</p>', '').replace('<br />', '').replace('<br/>', '')
            st.markdown(game_desc)
        else:
            selected_game_id = ""

# ------------- RATINGS PAGE -------------
elif add_selectbox == "Ratings":
    # Add the chart with the ratings here
    title_col.title("Ratings :bar_chart:")
    st.write("To be constructed")


# ------------- LOCATIONS PAGE -------------
elif add_selectbox == "Locations":
    title_col.title("Locations :pushpin:")
    st.write("To be constructed")

    # Add the map here
    '''loc_button = Button(label = "Get Location")
    loc_button.js_on_event("button_click", CustomJS(code = """
        navigator.geolocation.getCurrentPosition(
            (loc) => {
                document.dispatchEvent(new CustomEvent("GET_LOCATION", {detail: {lat: loc.coords.latitude, lon: loc.coords.longitude}}))
                }
            }
        )
        """))
    result = streamlit_bokeh_events(
        loc_button,
        events = "GET_LOCATION",
        key = "get_location",
        refresh_on_update = False,
        override_height = 75,
        debounce_time = 0
    )'''

    bestBuyLocationsList = []

    zipCode = ""

    while (True):
        zipCode = st.text_input("Please input your ZIP Code to display Best Buys near you: ")
        if zipCode.isdigit:
            break

    if zipCode != "":
        bestBuyLocationURL = "https://api.bestbuy.com/v1/stores((area(" + zipCode + ",10)))?apiKey=" + keys.BESTBUY_API_KEY + "&show=lng,lat,name&format=json"
        bestBuyLocations = requests.get(bestBuyLocationURL).json()
        bestBuyLocations
        for i in bestBuyLocations["stores"]:
            bestBuyLocationsList.append([i["lat"], i["lng"]])
        bestBuys = pd.DataFrame(np.array(bestBuyLocationsList), columns=['lat', 'lon'])
        bestBuys
        midpoint = (np.average(bestBuys['lat']), np.average(bestBuys['lon']))
        # st.pydeck_chart(pdk.Deck(
        #     map_style='mapbox://styles/mapbox/light-v9',
        #     initial_view_state=pdk.ViewState(
        #         latitude=midpoint[0],
        #         longitude=midpoint[1],
        #         zoom=11,
        #         pitch=0,
        #     ),
        #     layers=[
        #         # pdk.Layer(
        #         #     'HexagonLayer',
        #         #     data=bestBuys,
        #         #     get_position='[lon, lat]',
        #         #     radius=200,
        #         #     elevation_scale=4,
        #         #     elevation_range=[0, 1000],
        #         #     pickable=True,
        #         #     extruded=True,
        #         # ),
        #         pdk.Layer(
        #             'ScatterplotLayer',
        #             data=bestBuys,
        #             get_position='[lat, lon]',
        #             get_color='[255, 0, 156, 1]',
        #             get_radius=100,
        #         ),
        #     ],
        # ))
        st.map(bestBuys)

    # location = pd.DataFrame(result, columns = ("lat", "lon"))

# ------------- FEEDBACK PAGE -------------
elif add_selectbox == "Feedback":
    title_col.title("Feedback :memo:")

    username = st.text_input('Username')
    feedback = st.text_area('Feedback')

    usernameSuccess = False

    # If the Enter button is pressed...
    if st.button('Enter'):
        # If username is empty, show an error box
        if not username:
            st.error("Username is empty")
            usernameSuccess = False
        # Else, If username has a number & letter, show a success box
        elif any(i.isdigit() for i in username) & any(i.isalpha() for i in username):
            st.success("Username Accepted")
            usernameSuccess = True
        # Else (username is missing a number and/or letter), show an error box
        else:
            st.error("Username must contain both letters & numbers.")
            usernameSuccess = False

        # If the username is accepted...
        if (usernameSuccess):
            # If feedback is not empty, show an info box
            if (len(feedback.strip())):
                st.info("Feedback Saved")
            # Else (feedback is empty), show an error box
            else:
                st.error("The feedback is empty")

    # If an update is made without pressing the Enter button...
    else:
        # If username has a number & letter, show a success box
        if any(i.isdigit() for i in username) & any(i.isalpha() for i in username):
            st.success("Username Accepted")
        # Else (username is missing a number and/or letter), show an error box
        elif username:
            st.error("Username must contain both letters & numbers.")


# ------------- CONTACT INFO PAGE -------------
elif add_selectbox == "Contact Info":
    title_col.title("Contact Info :telephone_receiver:")
    st.write(
        "Further Assitance: [Get Help](https://www.bestbuy.com/site/electronics/customer-service/pcmcat87800050001.c?id=pcmcat87800050001&ref=212&loc=1&gclid=CjwKCAjwi6WSBhA-EiwA6Niokw2dEMikiJxDWkWZtjXiKCwS6qF1sTLZzMt-c9n7VaKOzXMFJbWT0xoCHtYQAvD_BwE&gclsrc=aw.ds)")
