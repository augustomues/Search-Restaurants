import streamlit as st
import pandas as pd
import numpy as np
import functions as fnc
from streamlit_folium import folium_static
import streamlit.components.v1 as components
import folium
from PIL import Image

st.set_page_config(page_title="Let's eat - Map", page_icon='🍽️', layout='wide', initial_sidebar_state='expanded')

df = pd.read_csv('result_cache.csv')

image = Image.open('Logo.png')

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.image(image, width=500)

col1, col2 = st.columns([4,1])
map_1 = folium.Map(location=[41.397356, 2.179490], zoom_start=13)
for i in df.index:
        restaurant = folium.Marker(location = [df['latitud'][i], df['longitud'][i]], popup=f"<a href='{df['url'][i]}'>asd</a>", tooltip=(df['name'][i]+", raiting: "+str(df['raiting'][i])+", reviews: "+str(df['total_reviews'][i])+", price level: "+ str(df['price_level'][i])))
        restaurant.add_to(map_1)
with col1:
    folium_static(map_1, width=700)

with col2:
    st.markdown("<h4>Go to the restaurant you are interesting in!</h4>", unsafe_allow_html=True)

    for i in df.index:
        st.markdown(f"<a style='color:red ' href='{df['url'][i]}'>{df['name'][i]}</a>", unsafe_allow_html=True)
