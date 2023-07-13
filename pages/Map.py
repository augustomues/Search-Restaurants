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
import Home

result = st.session_state.result

map_1 = folium.Map(location=[41.397356, 2.179490], zoom_start=13)
for i in result.index:
        restaurant = folium.Marker(location = [result['latitud'][i], result['longitud'][i]], tooltip=(result['name'][i]+", raiting: "+str(result['raiting'][i])+", reviews: "+str(result['total_reviews'][i])+", price level: "+ str(result['price_level'][i])))
        restaurant.add_to(map_1)

folium_static(map_1)