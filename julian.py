import math
import keys
import pandas as pd
import numpy as np
import requests
import streamlit as st
import geocoder

# This app is using Best Buy's API and RAWG Video Games Database API

# Title for this app
st.set_page_config(layout="wide", page_icon=":video_game:", page_title="Game Check")

blank, title_col, blank = st.columns([2, 3.5, 2])

# Side Bar
add_selectbox = st.sidebar.selectbox(
    "Select:",
    ["Homepage", "Ratings", "Locations", "Feedback", "Contact Info"]
)

# ------------- HOMEPAGE -------------
if add_selectbox == "Homepage":
    title_col.title("Game Check :video_game:")

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
    numSelections=0

    # Creates a streamlit multiselect widget to select what types of info the user would like to include in the table
    selectTableInfo = st.multiselect(
        'What info would you like to show on this list of games?',
        ['Genre', 'Rating', 'Release Date']
    )

    # If 'Genre' is selected on the above multiselect...
    # Creates a streamlit selectbox widget to select what genre the user would like to filter by
    if('Genre' in selectTableInfo):
        numSelections += 1
        selectGenre = st.selectbox(
            'What Genre would you like to search for?',
            ('All', 'Action', 'Adventure', 'Arcade', 'Board Games', 'Card', 'Casual', 'Educational', 'Family', 'Fighting',
             'Indie', 'Massively Multiplayer', 'Platformer', 'Puzzle', 'Racing', 'RPG', 'Simulation', 'Shooter', 'Sports', 'Strategy'),
            on_change=fixPage, args=("Reset",)
        )
    # Otherwise, set the selectGenre variable to 'Null'
    else:
        selectGenre = 'Null'

    # Add a query parameter for genres to the search, if requested by the user
    def doGenreSearch():
        if (selectGenre == 'All') | (selectGenre == 'Null'):
            return ""
        else:
            return "&genres=" + selectGenre.lower()

    # Creates a double-sided slider that lets the user provide a range of ratings to filter the results
    if('Rating' in selectTableInfo):
        numSelections += 2
        startRating, endRating = st.slider('Enter the range of Metacritic ratings',
                                        min_value=1,
                                        value=(1, 100),
                                        step=1,
                                        on_change=fixPage, args=("Reset",))

        st.info("Filtering by rating removes thousands of games that have no Metacritic rating")
    
    if('Release Date' in selectTableInfo):
        numSelections += 1

    # Add a query parameter for ratings to the search, if requested by the user
    def doRatingsSearch():
        if ('Rating' in selectTableInfo):
            return "&metacritic=" + str(startRating) + "," + str(endRating)
        else:
            return ""

    # The URL used for searching by game name, other queries
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
            itemToAppend = [i["name"]]
            columnItems = ['Game']

            for k in selectTableInfo:
                match k:
                    case 'Genre':
                        itemToAppend.insert(1, currGameGenres)
                        columnItems.insert(1, 'Genre')
                    case 'Release Date':
                        itemToAppend.insert(2, i["released"])
                        columnItems.insert(2, 'Released')
                    case 'Rating':
                            itemToAppend.append(i["metacritic"])
                            itemToAppend.append(i["ratings_count"])
                            columnItems.append('Rating')
                            columnItems.append('Number of Ratings')

            itemToAppend.append(i["id"])
            columnItems.append('Unique ID')

            if('Rating' in selectTableInfo):
                if (i["metacritic"] is None):
                    games_list.append(itemToAppend)
                elif ((i["metacritic"] >= startRating) & (i["metacritic"] <= endRating)):
                    games_list.append(itemToAppend)
            else:
                games_list.append(itemToAppend)

        # Empty out the currGameGenres string, to be filled out by the new game's genre data when the loop reiterates
        currGameGenres = ""

    # Create the table using the data pulled from the api
    if games_list:
        games_df = pd.DataFrame(
            games_list,
            columns=columnItems
        )
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

    # Display an image and lots of information for a selected game:
    if (games_list):
        select_game_options = ["..."]
        for i in range(len(games_df.index)):
            select_game_options.append(str(i) + " - " + str(games_list[i][0]))

        selected_game = st.selectbox('Select a game to learn more about:', select_game_options)
        selected_game_index = ""
        selected_game_id = ""

        if (selected_game != "..."):
            # Finds the correct index for the selected game in the list
            for j in range(len(selected_game)):
                if selected_game[j] != ' ':
                    selected_game_index += selected_game[j]
                    print(selected_game_index)
                else:
                    break

            # Finds the unique ID for the selected game
            print(1 + numSelections)
            selected_game_id = games_list[int(selected_game_index)][1 + numSelections]

            # Fetches info about a certain game from the API
            selected_game_url = "https://api.rawg.io/api/games/" + str(selected_game_id) + "?key=" + keys.RAWG_API_KEY
            print(selected_game_id)
            print(selected_game_url)

            selected_game_dict = requests.get(selected_game_url).json()

            img_col, desc_col = st.columns([0.8, 1])

            selected_game_platforms = ""
            selected_game_genres = ""
            selected_game_developers = ""

            # Populates information about platforms, genres, and developers
            for j in range(len(selected_game_dict["platforms"])):
                if (len(selected_game_platforms) == 0):
                    selected_game_platforms += selected_game_dict["platforms"][j]["platform"]["name"]
                else:
                    selected_game_platforms += ", " + selected_game_dict["platforms"][j]["platform"]["name"]

            for j in range(len(selected_game_dict["genres"])):
                if (len(selected_game_genres) == 0):
                    selected_game_genres += selected_game_dict["genres"][j]["name"]
                else:
                    selected_game_genres += ", " + selected_game_dict["genres"][j]["name"]

            for j in range(len(selected_game_dict["developers"])):
                if (len(selected_game_developers) == 0):
                    selected_game_developers += selected_game_dict["developers"][j]["name"]
                else:
                    selected_game_developers += ", " + selected_game_dict["developers"][j]["name"]

            with img_col:
                st.image(selected_game_dict["background_image"], width=620)
            with desc_col:
                st.header(selected_game_dict["name"])
                st.text("Rating: " + str(selected_game_dict["rating"]))
                st.markdown(selected_game_dict["description_raw"])
                st.text("Released: " + selected_game_dict["released"])
                st.text("Genres: " + str(selected_game_genres))
                st.text("Developers: " + str(selected_game_developers))
                st.text("Platforms: " + str(selected_game_platforms))
        else:
            selected_game_id = ""

# ------------- RATINGS PAGE -------------
elif add_selectbox == "Ratings":
    # Add the chart with the ratings here
    title_col.title("Ratings :bar_chart:")
    
    # Search name for game
    game_to_search_for = st.text_input('Enter the name of the game you would like to search for:')
    currPage = 1

    if game_to_search_for:
        # Used to replace spaces in a search with +'s, so that the URL actually works
        def fixForURL(string):
            string = string.replace(" ", "+")
            return string


        # The URL used for searching by game name
        # TODO: The URL here should be using Best Buy's API, not RAWG. The RAWG API should be used solely for metadata like ratings, genre, etc.
        games_url = "https://api.rawg.io/api/games?key=" + keys.RAWG_API_KEY + "&search=" + fixForURL(
            game_to_search_for)
        print("The URL of the API request:" + games_url)

        # Creates a dictionary (like an array but the indexes are "keys" (strings) rather than integers) using info returned from the URL request
        games_dict = requests.get(games_url).json()
        game_options = games_dict["results"]

        select_game_options = []
        for i in range(len(game_options)):
            select_game_options.append(str(game_options[i]["name"]))

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

        st.write("Ratings Distribution for {0}".format(game_to_search_for))
        chart_data = pd.DataFrame(ratings_list)
        st.bar_chart(data=chart_data, width=0, height=0, use_container_width=True)

    #TODO: Format bar chart so it displays all the data in the frame that is visible to the user. If it is too zoomed in by default, then the user won't be able to see all the data

# ------------- LOCATIONS PAGE -------------
elif add_selectbox == "Locations":
    title_col.title("Locations :pushpin:")

    searchByZIP = st.checkbox("Search by specific ZIP Code instead of your location?")

    bestBuyLocationsList = []
    zipCode = ""

    # Search by user-provided ZIP Code
    if(searchByZIP):
        while(True):
            zipCode = st.text_input("Please input your ZIP Code to display Best Buys near you: ")
            if zipCode.isdigit:
                break

        if zipCode != "":
            # The URL used for searching for best buy locations near the provided ZIP Code
            bestBuyLocationURL = "https://api.bestbuy.com/v1/stores((area(" + zipCode + ",10)))?apiKey=" + keys.BESTBUY_API_KEY + "&show=lng,lat,name&format=json"
            bestBuyLocations = requests.get(bestBuyLocationURL).json()
            
            st.info("Currently displaying Best Buy Locations within a 10 mile square of provided ZIP Code")


            if(not 'error' in bestBuyLocations):
                # Best Buy Locations within 10 mile square of provided ZIP Code
                for i in bestBuyLocations["stores"]:
                    bestBuyLocationsList.append([i["lat"], i["lng"]])
                
                if(bestBuyLocationsList):
                    bestBuys = pd.DataFrame(np.array(bestBuyLocationsList), columns = ['lat', 'lon'])
                    midpoint = (np.average(bestBuys['lat']), np.average(bestBuys['lon']))

                    st.map(bestBuys)
                else:
                    st.error("No Best Buys were found near that ZIP Code")
            else:
                    st.error("The ZIP Code you entered is invalid")
    # Search by user's actual location
    else:
        showNearestOnly = st.checkbox("Only Show Nearest Store")
        
        # Get user location (latitude and longitude)
        g = geocoder.ip('me')
        userLat = g.latlng[0]
        userLong = g.latlng[1]

        # The URL used for searching for best buy locations near user's lat and long
        bestBuyLocationURL = "https://api.bestbuy.com/v1/stores((area(" + str(userLat) + "," + str(userLong) + ",10)))?apiKey=" + keys.BESTBUY_API_KEY + "&show=lng,lat,name&format=json"
        bestBuyLocations = requests.get(bestBuyLocationURL).json()

        if(showNearestOnly):
            # Only nearest Best Buy Location
            for i in bestBuyLocations["stores"]:
                bestBuyLocationsList.append([i["lat"], i["lng"]])
                break
            
            st.info("Currently displaying Nearest Best Buy Location to you")
        else:
            # Best Buy Locations within 10 mile square of User's location
            for i in bestBuyLocations["stores"]:
                bestBuyLocationsList.append([i["lat"], i["lng"]])
            
            st.info("Currently displaying Best Buy Locations within a 10 mile square of you")

        if(bestBuyLocationsList):
            bestBuys = pd.DataFrame(np.array(bestBuyLocationsList), columns = ['lat', 'lon'])
            midpoint = (np.average(bestBuys['lat']), np.average(bestBuys['lon']))

            st.map(bestBuys)
        else:
            st.error("No Best Buys were found near your loation")

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
