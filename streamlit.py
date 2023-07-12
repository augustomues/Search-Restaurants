import streamlit as st
import pandas as pd
import numpy as np
import functions as fnc

st.set_page_config(page_title="Restaurant Selector", layout='centered', initial_sidebar_state='auto')

st.markdown("<h1 style='text-align: center; color: black; font-size: 2em'>Welcome to Barcelona Restaurant Selector</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2,6,2])
with col1:
    st.write("")
with col2:
    st.image("https://t1.uc.ltmcdn.com/es/posts/7/1/6/como_disfrutar_un_fin_de_semana_en_barcelona_24617_600.jpg")
with col3:
    st.write("")

st.markdown("<h1 style='text-align: center; color: black; font-size: 22px'>Not sure where to go to eat or drink?</h1>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: black; font-size: large'>Let's get started!</h1>", unsafe_allow_html=True)

df_1 = pd.read_csv('data/barc_restaurants.csv')
df_2 = pd.read_csv('data/place_details.csv')

for i in df_2.columns[9:]:
    df_2[i] = df_2[i].apply(lambda x: fnc.converting_times_to_ranges(x))

df = df_1.merge(df_2, how='inner', on='place_id')

distritos = list(df['distritos'].unique())
barrios = list(df['neightbour'].unique())
hours = np.arange(1, 25)

st.markdown("<h3> Please filter based on your needs.</h3><h6 style='font-size: 12px'>*Bare in mind that not all filters are needed. You can leave some fields empty.</h6>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center'>Let's start by the most important:</h3>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([6, 1, 6])
vegeterian_opt =  []
beer_option = []
dine_in_option = []
takeout_option = []
wine_option = []
wheelchair_available = []
reservable = []
days = []

with col1:
    price_max = st.slider("Which is the maximun price level you are looking for? Where 1=$ and 4=$$$$", 4, 1)
    min_reviews = st.slider("How many reviews you want the restaurant to have at least?", 30000, 0, step=500)
    avg_raiting = st.slider("What is the minimun avg. raiting you are looking for", 5.0, 0.0, step=0.1)

with col3:
    districts = st.multiselect('In which districts would you like to eat?', options=distritos)
    neightbours = st.multiselect('To which Neightbour do you want to go?', options=barrios)
    days = st.selectbox('Which day?', options=['Any', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    hour = st.selectbox('At what time?', options=hours)

st.markdown("<h3 style='text-align: center'>Do you have some extra requirments?</h3>", unsafe_allow_html=True)

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
    wheelchair_available = st.multiselect('Wheelchair accesible?', options=['Yes', 'No', 'Maybe'])

st.dataframe(fnc.restaurant_selector(df, raiting=avg_raiting, max_price=price_max, total_reviews=min_reviews,
                       neightbour=neightbours, district=districts, dine_in=dine_in_option, reservable=reservable,
                        serves_beer=beer_option, serves_wine=wine_option, vegetarian=vegeterian_option, takeout=takeout_option,
                        wheelchair_accessible=wheelchair_available, day=days, time=hour, sorter=None, limit=10))


    
