<h1>Search Restaurants<h1>

<h2>Introduction</h2>

<p>Welcome to Search Restaurants. This repo is about my Final Project of the Data Analytics Bootcamp I did in Ironhack.<br>
The idea of the project was to get valuable data from all restaurants currelty avaiable in Barcelona (June 2023) in order to be able to create an App that allows the user to search for restarants based on <u>more advanced filters.</u> For that we have created <b>Let's eat!</b><br>
However, before introducing the App, let's take a look at how the repo is organized.</p>

<h2>Repo organization</h2>

<p>On this repo you will be able to find the following directories/files:<br><br>
1. <u>data directory:</u> This filder contains all the csv files use on the project. In total we have 6:<br>
a) barc_restaurants.csv: contains all the resutarants in Barcelona. For this I have used the <a href='https://developers.google.com/maps/documentation/places/web-service/search-find-place?hl=es-419'>API Place Search -> Find Place</a> (the coordinates used to iterate is located on the following file) <br>
b) Barcelona_coordinates.csv: This file contains equally separeted points (lon;lat) of barcelona, separeted approximately by 80m. This is used for iteration when calling the main API mentioned above.<br>
c) place_details.csv: contains details of the restaurants that were not available on the main API, such as if the restaurant serves beer, opening hours and days, etc. For this I have used the <a href='https://developers.google.com/maps/documentation/places/web-service/details?hl=es-419'>API Place Details</a><br>
d) restaurants_reviews.csv: It contains (if available) the top 5 more relevant reviews for each restaurant<br>
e) restaurants_url.csv: it contains the google maps url for each restaurant
f) result_cache.csv: it store information generated on the Streamlit main page in order to be passed to the Map page<br><br>
2. <u>Figures directory:</u> It contains 6 different visualization generated on Python. This views are actaulyl available on the dashboard. It also contain the logo of the App.<br><br>
3. <u>Geojsons directory:</u> It contains the district and neighborhood geojsons of Barcelona. The non original ones were modified in order to be a list of documents and allow us to connect to Mongo. but files (original and non-original) are pretty much the same.<br><br>
4. <u>functions.py:</u> Main python file containing all the functions used on Main and Home<br><br>
5. <u>Home.py:</u> This file is the Streamlit one. Is the main page. We also have the <u>page directory</u> containing the Map.py file, which is the second page of the Streamlit.<br><br>
6. <u>main.ipynb:</u> Notebook used for the ETL/EDI and the visualizations.<br><br>
7. <u>requirments.txt:</u> It contains all the libraries and their versions used on this project
</p>

<h2>Process flow</h2>

As most of the projects, this one start start getting the data. As already explained, for that we have used two APIs from google maps (we have >300eur credits for free). Then, data is loaded into SQL (and alternative I have also created the csv files so it can be available to everybody). We have the created some visualizations and dashboard (using PowerBi). Lately, and the ultimate product of this repo, we have created the Streamlit App, located in Home.py.
<h2>Analysis</h2>
As I coulnd't publish the PowerBi dashboard, leaving here some visuals I have manage to create:
<img src='Figures/Dashboard captures/Dashboard Page1.png'>
<img src='Figures/Dashboard captures/Dashboard Page2.png'>
<img src='Figures/Dashboard captures/Dashboard Page3.png'>
This help us understand how is the restaurant market in Barcelona (how many restaurants we have per neighbour and per district, what is the average raiting, the pricing level, etc).
From the last visualization, each burble is one neighbour, and the size of it tell us how many restaurant the neighbour has. The color refers to each district. If we want cheap and good restaurants, we should look at top left burbles. While if we want fancy places, top right.<br><br>
For instante, San Marti (yellow burbles) district have plenty of restaurants with high raiting and low price, while Eixample (blue burbles) has more fancy restauratns (with good quality as well).
<h2>Let's it!</h2>
<img src='Figures/Logo.png'>

This is the ultimate product of the project. It was built on Streamlit.<br>
If you are interesting on running it, suggest you pulling this repo, installing the requirments.txt on your own environment and on the main directory open your git/command prompt and run the code:<br>
<pre>streamlit run Home.py</pre>
<b>WHY LET'S EAT?</b><br>
Basically, whenever you want to go to a bar/restaurant, you either recall some suggestion someone gave you, or you got to a place you have already gone. But what if you want something new?<br>
Well probably you will go to Google Maps and try searching for a place. However, the fitlers you can apply there are very limited. See below:
<img src='Figures/GoogleMaps filters.PNG'><br>
So what if you want extra filters, such as spcific day/hours, total reviews, vegeterian places, serves beer/wine, etc, etc? Now, with Let's eat, this is solved.

Leaving here some screeshoots taken:

<img src='Figures/Streamlit captures/Snapshoot_1.png'>
<img src='Figures/Streamlit captures/Snapshoot_2.png'>
<img src='Figures/Streamlit captures/Snapshoot_3.png'>
<img src='Figures/Streamlit captures/Snapshoot_4.png'>
<img src='Figures/Streamlit captures/Snapshoot_5.png'>
<img src='Figures/Streamlit captures/Snapshoot_6.png'>

And that's it! Now, you can navigate through the dashboard to understand how the restaurant market in Barcelona is, and then you can start searching for the best restaurant!<br><br>
Hope you have enjoyed as much as I have doing this project.<br><br>
If you have any question, feel free to reach me on <a href='https://www.linkedin.com/in/augusto-jos%C3%A9-mues-1581b717b/'>Linkedin</a>