# Game Check

## About
Game Check is a website that allows its user to find information about specified video games; sort games by their attributes such as game name, genre, ratings, and/or release date; compare games by their ratings; and find Best Buy locations near the user to find the nearest store to buy games.

The website uses the [RAWG Video Games Database API](https://rawg.io/apidocs) for the components of the site regarding video games, and uses the [Best Buy Stores API](https://bestbuyapis.github.io/api-documentation/#stores-api) to display a map of Best Buy locations, according to the user's ZIP code or any ZIP code specified by the user.


## Running Game Check

In order to run Game Check, you will first need to have Git & Python on your machine. Below are the download links to both:
* Git: https://git-scm.com/downloads
* Python: https://www.python.org/downloads/

Next, you will need to clone this Github repository onto your PC.

You can do this by running the following command in your terminal of choice while in your preferred path: <br />
`git clone https://github.com/ricardocolom64/HCI-VideoGameApp.git`

Once the repository is finished installing, you will need to enter the repository directory and install several python libraries that are necessary to run the app by running the following commands:

* Streamlit: `pip install streamlit`
* Geocoder: `pip install geocoder`
* Plotly: `pip install plotly`

Once you have completed all of the above steps, you may run the website by running the command: `streamlit run main.py`.
