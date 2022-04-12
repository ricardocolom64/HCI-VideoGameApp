import keys
import pandas as pd
import numpy as np
import requests
import streamlit as st
#from streamlit_bokeh_events import streamlit_bokeh_events
#from bokeh.models.widgets import Button
#from bokeh.models import CustomJS
import pydeck as pdk


# This app is using Best Buy's API and RAWG Video Games Database API

# Title for this app
st.set_page_config(layout="wide", page_icon=":video_game:", page_title="Video Game App")

blank, title_col, blank = st.columns([2,3.5,2])


# Side Bar
add_selectbox = st.sidebar.selectbox(
  "Select:",
  ["Homepage", "Ratings", "Locations", "Feedback","Contact Info"]
)

# ------------- HOMEPAGE -------------
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
    games_url = "https://api.rawg.io/api/games?key=" + keys.RAWG_API_KEY + "&search=" + fixForURL(
        game_to_search_for) + "&page=" + str(currPage)
    print("The URL of the API request:" + games_url)

    # Creates a dictionary (like an array but the indexes are "keys" (strings) rather than integers) using info returned from the URL request
    games_dict = requests.get(games_url).json()

    games_list = []
    currGameGenres = ""

    # Creates a streamlit multiselect widget to select what types of info the user would like to include in the table
    selectTableInfo = st.multiselect(
        'What info would you like to show on this list of games?',
        ['Genre', 'Rating', 'Release Date']
    )

    # If 'Genre' is selected on the above multiselect...
    # Creates a streamlit selectbox widget to select what genre the user would like to filter by
    if('Genre' in selectTableInfo):
        selectGenre = st.selectbox(
            'What Genre would you like to search for?',
            ('All', 'Action', 'Adventure', 'Arcade', 'Platformer', 'RPG', 'Racing', 'Sports')
        )
    # Otherwise, set the selectGenre variable to 'Null'
    else:
        selectGenre = 'Null'

    # Creates a double-sided slider that lets the user provide a range of ratings to filter the results
    if('Rating' in selectTableInfo):
        startRating, endRating = st.select_slider('Enter the range of ratings',
                                                  options=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
                                                  value=(1.0,4.0))

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

            #instead of the elif branch, i used a switch statement here to make things more readable and efficient; it functions more or less identically -Martin
            itemToAppend = [i["name"]]

            for k in selectTableInfo:
                match k:
                    case 'Genre':
                        itemToAppend.insert(1, currGameGenres)
                    case 'Release Date':
                        itemToAppend.append(i["released"])
                    case 'Rating':
                        if i["released"] in itemToAppend:
                            itemToAppend.insert(itemToAppend.index(i["released"]) + 1, i["rating"])
                            itemToAppend.insert(itemToAppend.index(i["rating"]) + 1, i["ratings_count"])
                        else:
                            itemToAppend.append(i["rating"])
                            itemToAppend.append(i["ratings_count"])

            itemToAppend.append(i["id"])

            #print(itemToAppend) this is debugging code

            #there's a better way of doing this but it didn't work so here's the bad solution
            if('Rating' in selectTableInfo):
                if ((i["rating"] >= startRating) & (i["rating"] <= endRating)):
                    games_list.append(itemToAppend)
            else:
                games_list.append(itemToAppend)


            # # If selectTableInfo multiselect includes Genre, Release Date, and Ratings
            # if ('Genre' in selectTableInfo) & ('Release Date' in selectTableInfo) & ('Rating' in selectTableInfo):
            #     # Adds game to results list if the rating is in the range provided by the user
            #     if((i["rating"] >= startRating) & (i["rating"] <= endRating)):
            #         games_list.append([i["name"], currGameGenres, i["released"], i["rating"], i["ratings_count"], i["id"]])

            # # If selectTableInfo multiselect includes Genre, Release Date
            # elif ('Genre' in selectTableInfo) & ('Release Date' in selectTableInfo):
            #     games_list.append([i["name"], currGameGenres, i["released"], i["id"]])

            # # If selectTableInfomultiselect includes Genre, Ratings
            # elif ('Genre' in selectTableInfo) & ('Rating' in selectTableInfo):
            #     # Adds game to results list if the rating is in the range provided by the user
            #     if ((i["rating"] >= startRating) & (i["rating"] <= endRating)):
            #         games_list.append([i["name"], currGameGenres, i["rating"], i["ratings_count"], i["id"]])


            # # If selectTableInfomultiselect includes Release Date, and Ratings
            # elif ('Release Date' in selectTableInfo) & ('Rating' in selectTableInfo):
            #     # Adds game to results list if the rating is in the range provided by the user
            #     if ((i["rating"] >= startRating) & (i["rating"] <= endRating)):
            #         games_list.append([i["name"], i["released"], i["rating"], i["ratings_count"], i["id"]])

            # # If selectTableInfo multiselect only includes Genre
            # elif ('Genre' in selectTableInfo):
            #     games_list.append([i["name"], currGameGenres, i["id"]])

            # # If selectTableInfo multiselect only includes Release Date
            # elif ('Release Date' in selectTableInfo):
            #     games_list.append([i["name"], i["released"], i["id"]])

            # # If selectTableInfo multiselect only includes Ratings
            # elif ('Rating' in selectTableInfo):
            #     # Adds game to results list if the rating is in the range provided by the user
            #     if ((i["rating"] >= startRating) & (i["rating"] <= endRating)):
            #         games_list.append([i["name"], i["rating"], i["ratings_count"], i["id"]])

            # # If selectTableInfo multiselect doesn't include any options
            # else:
            #     games_list.append([i["name"], i["id"]])

        # empty out the currGameGenres string, to be filled out by the new game's genre data when the loop reiterates
        currGameGenres = ""


    #the elif branches were bothering me so I condensed the whole thing into this method that is absolutely gross and shouldn't work as well as it does but it does and that's what matters -Martin

    #so first we make a list of columns including game and unique id since those are always gonna be in the results
    frameColumns = ['Game', 'Unique ID']

    #we add to this list everything that the user selected earlier in the multiselect
    for i in selectTableInfo:
        frameColumns.append(i)

    #we use the sort method because as it turns out the table columns order we want is almost in alphabetical order
    frameColumns.sort()
    print(frameColumns)

    #we add the number of ratings column
    if 'Rating' in frameColumns:
        frameColumns.insert(frameColumns.index('Rating') + 1, 'Number of Ratings')
    #and also put released behind rating 
    if ('Release Date' in frameColumns) & ('Rating' in frameColumns):
        frameColumns.insert(frameColumns.index('Rating'), frameColumns.pop(frameColumns.index('Release Date')))

    print(frameColumns)
    #and then we create the dataframe to print, converting 45 lines of code to 21
    games_df = pd.DataFrame(
        games_list,
        columns = frameColumns
    )
        


    # if ('Genre' in selectTableInfo) & ('Release Date' in selectTableInfo) & ('Rating' in selectTableInfo):
    #     games_df = pd.DataFrame(
    #         games_list,
    #         columns=('Game', 'Genre', 'Released', 'Rating', 'Number of Ratings', 'Unique ID'))

    # # If the data filled into games_list includes Genre and Release Date
    # elif ('Genre' in selectTableInfo) & ('Release Date' in selectTableInfo):
    #     games_df = pd.DataFrame(
    #         games_list,
    #         columns=('Game', 'Genre', 'Released', 'Unique ID'))

    # # If the data filled into games_list includes Genre and Ratings
    # elif ('Genre' in selectTableInfo) & ('Rating' in selectTableInfo):
    #     games_df = pd.DataFrame(
    #         games_list,
    #         columns=('Game', 'Genre', 'Rating', 'Number of Ratings', 'Unique ID'))

    # # If the data filled into games_list includes Release Date and Ratings
    # elif ('Release Date' in selectTableInfo) & ('Rating' in selectTableInfo):
    #     games_df = pd.DataFrame(
    #         games_list,
    #         columns=('Game', 'Release Date', 'Rating', 'Number of Ratings', 'Unique ID'))

    # # If the data filled into games_list includes Genre
    # elif ('Genre' in selectTableInfo):
    #     games_df = pd.DataFrame(
    #         games_list,
    #         columns=('Game', 'Genre', 'Unique ID'))

    # # If the data filled into games_list includes Release Date
    # elif ('Release Date' in selectTableInfo):
    #     games_df = pd.DataFrame(
    #         games_list,
    #         columns=('Game', 'Released', 'Unique ID'))

    # # If the data filled into games_list includes Ratings
    # elif ('Rating' in selectTableInfo):
    #     games_df = pd.DataFrame(
    #         games_list,
    #         columns=('Game', 'Rating', 'Number of Ratings', 'Unique ID'))

    # # If the data filled into games_list does not include Genre, Release Date, or Ratings
    # else:
    #     games_df = pd.DataFrame(
    #         games_list,
    #         columns=('Game', 'Unique ID'))

    st.dataframe(games_df)


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
    # loc_button = Button(label = "Get Location")
    # loc_button.js_on_event("button_click", CustomJS(code = """
    #     navigator.geolocation.getCurrentPosition(
    #         (loc) => {
    #             document.dispatchEvent(new CustomEvent("GET_LOCATION", {detail: {lat: loc.coords.latitude, lon: loc.coords.longitude}}))
    #             }
    #         }
    #     )
    #     """))
    # result = streamlit_bokeh_events(
    #     loc_button,
    #     events = "GET_LOCATION",
    #     key = "get_location",
    #     refresh_on_update = False,
    #     override_height = 75,
    #     debounce_time = 0
    # )

    bestBuyLocationsList = []

    zipCode = ""

    while(True):
        zipCode = st.text_input("Please input your ZIP Code to display Best Buys near you: ")
        if zipCode.isdigit:
            break
    
    if zipCode != "":
        bestBuyLocationURL = "https://api.bestbuy.com/v1/stores((area(" + zipCode + ",20)))?apiKey=" + keys.BESTBUY_API_KEY + "&show=lng,lat,name&format=json"
        bestBuyLocations = requests.get(bestBuyLocationURL).json()
        #bestBuyLocations
        for i in bestBuyLocations["stores"]:
            bestBuyLocationsList.append([i["lat"], i["lng"]])
        bestBuys = pd.DataFrame(np.array(bestBuyLocationsList), columns = ['lat', 'lon'])
        #bestBuys this was for debugging
        midpoint = (np.average(bestBuys['lat']), np.average(bestBuys['lon']))
        
        # st.pydeck_chart(pdk.Deck( disgusting and horrid
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


    #location = pd.DataFrame(result, columns = ("lat", "lon"))
    
    


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
