import streamlit as st
import pandas as pd
import numpy as np
import functions as fnc
from streamlit_folium import folium_static
import streamlit.components.v1 as components
import codecs
import requests
import folium
from PIL import Image

st.set_page_config(page_title="Restaurant Selector", page_icon='🍽️', layout='centered', initial_sidebar_state='expanded')
df_1 = pd.read_csv('data/barc_restaurants.csv')
df_2 = pd.read_csv('data/place_details.csv')
for i in df_2.columns[9:]:
    df_2[i] = df_2[i].apply(lambda x: fnc.converting_times_to_ranges(x))
df = df_1.merge(df_2, how='inner', on='place_id')
distritos = list(df['distritos'].unique())
distritos.remove('Not found')
barrios = list(df['neightbour'].unique())
barrios.remove('Not found')
hours = np.arange(1, 25)
vegeterian_opt =  []
beer_option = []
dine_in_option = []
takeout_option = []
wine_option = []
wheelchair_available = []
reservable = []
days = []


image = Image.open('Logo.png')

st.image(image, width=700)

st.markdown("<h1 style='text-align: center'>Welcome to Barcelona Restaurant Selector</h1>", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center'>Not sure where to go to eat or drink? --> Let's eat! 🍽️</h3>", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: left; text-decoration:underline'>Who are we?</h3>", unsafe_allow_html=True)
st.markdown("<h6 style='text-align: left'>Introducing Let's eat! The ultimate restaurant selector in Barcelona. We understand that finding the perfect place to dine can be overwhelming considering the countless options available. That's where we come in. Let's eat is a user-friendly app designed to simplify your culinary journey by providing a comprehensive database of restaurants in Barcelona. With our powerful filtering system, you can effortlessly narrow down your search based on your specific preferences, be it cuisine type, price range, ambiance, dietary restrictions, or any other criteria that matter to you.</h6>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: left; text-decoration:underline'>Why us?</h3>", unsafe_allow_html=True)
st.markdown("<h6 style='text-align: left'>⚡ Let's eat can instantly provide you with the best places that adapt to your needs.<br>💰 Every search counts: For the love of food and the planet, we donate 1€ to WWF.<br>🍔 We have more than 5000 options for you. In one single place!</h6>", unsafe_allow_html=True)
st.markdown("<h3> Intersting on trying this out? Let's get started!</h3>", unsafe_allow_html=True)

with st.form("my_form"):
    st.markdown("<h3 style='text-align: center'>Please filter based on your needs:</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([6, 1, 6])
    with col1:
        price_max = st.slider("Which is the price level you are looking for? Where 1=$ and 4=$$$$", 1, 4, (1, 2), help='Will display all restaurants with price level between 1 and the selected value here')[1]
        min_reviews = st.slider("How many reviews you want the restaurant to have at least?", 0, 15000, (750,15000),step=250, help='Will display all restaurants where their total reviews is higher that the value selected. Restaurants with less reviews will not be displayed')[0]
        avg_raiting = st.slider("What is the minimun avg. raiting you are looking for?", 0.0, 5.0, (3.5, 5.0), step=0.1, help='Will display all restaurants with avg. raiting above the value selected. Restaurants with less raiting, will not be displayed')[0]

    with col3:
        districts = st.multiselect('In which districts would you like to eat?', options=distritos)
        neightbours = st.multiselect('To which Neightbour do you want to go?', options=barrios)
        days = st.selectbox('Which day?', options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        hour = st.selectbox('At what time?', options=hours)

    st.markdown("<h3 style='text-align: center'>Do you have some extra requirments?</h3>", unsafe_allow_html=True)
    st.markdown("<h10 style='text-align: center'>*Please take into account that excess on filters may end up not finding any restaurant. Just choose those filters you really need. </h10>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        vegeterian_option = st.multiselect('Vegeterian?', options=['Yes', 'No', 'Maybe'])
        beer_option = st.multiselect('Serves beer?', options=['Yes', 'No', 'Maybe'])
    with col2:
        dine_in_option = st.multiselect('Dine In?', options=['Yes', 'No', 'Maybe'])
        takeout_option = st.multiselect('Takeout?', options=['Yes', 'No', 'Maybe'])
        reservable = st.multiselect('Reservable?', options=['Yes', 'No', 'Maybe'])
    with col3:
        wine_option = st.multiselect('Serves wine?', options=['Yes', 'No', 'Maybe'])
        wheelchair_accessible = st.multiselect('Wheelchair accesible?', options=['Yes', 'No', 'Maybe'])



    st.markdown("<h3 style='text-align: center'>Now time to order the data:</h3>", unsafe_allow_html=True)

    limit = st.number_input('How many options do you maximum want?', value=10)
    sorter = st.multiselect('How do you want to sort the output?', options=['total_reviews', 'price_level', 'raiting'])

    submitted = st.form_submit_button("Suggest me restaurants")

col1, col2, col3 = st.columns(3)

with col1:
   st.image("https://www.reasonwhy.es/media/library/supermercado_glovo.png")

with col2:
   st.image("https://www.themarkethink.com/wp-content/uploads/2019/09/toks-uber-eats.jpg")

with col3:  
   st.image("https://www.marketingdirecto.com/wp-content/uploads/2019/05/mcdonalds.jpg")

result = fnc.restaurant_selector(df, raiting=avg_raiting, max_price=price_max, total_reviews=min_reviews,
                       neightbour=neightbours, district=districts, dine_in=dine_in_option, reservable=reservable,
                        serves_beer=beer_option, serves_wine=wine_option, vegetarian=vegeterian_option, takeout=takeout_option,
                        wheelchair_accessible=wheelchair_accessible, day=days, time=hour, sorter=sorter, limit=limit)


st.markdown("<h3 style='text-align: left'>Restaurants suggested:</h3>", unsafe_allow_html=True)

st.dataframe(result[['name', 'raiting', 'price_level', 'total_reviews', 'neightbour', 'distritos', 'direction']])
    
# Updates
st.session_state.result = result