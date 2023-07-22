import streamlit as st
import pandas as pd
import numpy as np
import functions as fnc
from streamlit_folium import folium_static
from PIL import Image


st.set_page_config(page_title="Let's eat", page_icon='🍽️', layout='wide', initial_sidebar_state='expanded')
df_1 = pd.read_csv('data/barc_restaurants.csv')
df_2 = pd.read_csv('data/place_details.csv')
df_3 = pd.read_csv('data/restaurants_urls.csv')
df_4 = pd.read_csv('data/restaurants_reviews.csv', encoding='latin-1')

for i in df_2.columns[9:]:
    df_2[i] = df_2[i].apply(lambda x: fnc.converting_times_to_ranges(x))
df_m_1 = df_1.merge(df_2, how='inner', on='place_id')
df = df_m_1.merge(df_3, how='inner', on='place_id')
distritos = list(df['distritos'].unique())
distritos.remove('Not found')
df_4['ethnicity'] = df_4['reviews'].apply(fnc.get_food)
df_grouped = df_4.groupby('place_id')['ethnicity'].agg(fnc.aggregate_ethnicity).reset_index()
df = df.merge(df_grouped, how='left', on='place_id')

hours = np.arange(1, 25)
vegeterian_opt =  []
beer_option = []
dine_in_option = []
takeout_option = []
wine_option = []
wheelchair_available = []
reservable = []
days = []
related_dishes = {
    'Burger': ['Burger', 'Hamburger', 'Smash'],
    'Argentinian/Uruguayan': ['Argentina', 'Argentinian', 'Uruguay', 'Uruguayan', 'Empanada', 'Asado', 'Milanesa', 'Escalope'],
    'Chinese': ['China', 'Chinese', 'Dim Sum', 'Peking Duck', 'Kung Pao Chicken', 'Hot Pot', 'Mapo Tofu'],
    'Italian': ['Italy', 'Italian', 'Pasta', 'Pizza', 'Carbonara', 'Lasagna', 'Tiramisu'],
    'Spanish': ['Spain', 'Spanish', 'Paella', 'Tapas', 'Sangria', 'Gazpacho', 'Churros'],
    'Mexican': ['Mexico', 'Mexican', 'Tacos', 'Guacamole', 'Enchiladas', 'Chiles Rellenos', 'Mole'],
    'Japanese': ['Japan', 'Japanese', 'Sushi', 'Ramen', 'Tempura', 'Sashimi', 'Matcha'],
    'Indian': ['India', 'Indian', 'Curry', 'Naan', 'Biryani', 'Tandoori', 'Gulab Jamun'],
    'Korean': ['Korea', 'Korean', 'Kimchi', 'Bulgogi', 'Bibimbap', 'Korean BBQ', 'Japchae'],
    'Thai': ['Thailand', 'Thai', 'Pad Thai', 'Tom Yum', 'Green Curry', 'Mango Sticky Rice', 'Som Tum'],
    'Peruvian': ['Peru', 'Peruvian', 'Ceviche', 'Lomo Saltado', 'Aji de Gallina', 'Anticuchos', 'Pisco Sour'],
    'Greek': ['Greece', 'Greek', 'Moussaka', 'Souvlaki', 'Tzatziki', 'Dolmades', 'Baklava'],
    'French': ['France', 'French', 'Croissant', 'Escargot', 'Coq au Vin', 'Ratatouille', 'Crème Brûlée']  
}

distr_neight = df[['distritos', 'neightbour']].drop_duplicates()


image = Image.open('Figures/Logo.png')

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.image(image, width=500)


#st.dataframe(df)
st.markdown("<h1 style='text-align: center'>Welcome to Barcelona Restaurant Selector</h1>", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center'>Not sure where to go to eat or drink? 👉 <strong>Let's eat!</strong>🍽️</h3>", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: left; text-decoration:underline'>Who are we?</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: left'>Introducing <strong>Let's eat! </strong>The ultimate restaurant selector in Barcelona. We understand that finding the perfect place to dine can be overwhelming considering the countless options available. That's where we come in. Let's eat is a <strong>user-friendly app</strong> designed to simplify your culinary journey by providing a comprehensive database of <strong>restaurants in Barcelona</strong>. With our powerful filtering system, you can effortlessly <strong>narrow down your search</strong> based on your specific preferences, be it cuisine type, price range, ambiance, dietary restrictions, or any other criteria that matter to you.</p>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: left; text-decoration:underline'>Why us?</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: left'>⚡ Let's eat can instantly provide you with the best places that adapt to your needs.<br>💰 Every search counts: For the love of food and the planet, we donate 1€ to WWF.<br>🍔 We have more than 5000 options for you. In one single place!</p>", unsafe_allow_html=True)
st.markdown("<h3> Intersting on trying this out? Let's get started!</h3>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; text-decoration:underline'> Quick map for reference:</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    folium_static(fnc.plot_restaurants(df))

with st.form("my_form1"):
    st.markdown("<h3>1. Is there any district or type of food you are looking for?</h3>", unsafe_allow_html=True)
    districts = st.multiselect('If not, just leave this blank and click "Proceed" on below bottom', options=distritos)
    types_of_food = st.multiselect("What type of food would you like to eat?", options=related_dishes.keys())
    submitted = st.form_submit_button("Proceed")

if districts == []:
    districts = distritos

with st.form("my_form"):
    st.markdown("<h3>2. Please select based on your needs</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([6, 1, 6])
    with col1:
        price_max = st.slider("Which is the price level you are looking for? Where 1=$ and 4=$$$$", 1, 4, (1, 2), help='Will display all restaurants with price level between 1 and the selected value here')[1]
        min_reviews = st.slider("How many reviews you want the restaurant to have at least?", 0, 15000, (750,15000),step=250, help='Will display all restaurants where their total reviews is higher that the value selected. Restaurants with less reviews will not be displayed')[0]
        avg_raiting = st.slider("What is the minimun avg. raiting you are looking for?", 0.0, 5.0, (3.5, 5.0), step=0.1, help='Will display all restaurants with avg. raiting above the value selected. Restaurants with less raiting, will not be displayed')[0]

    with col3:
        neightbours = st.multiselect('To which Neightbour do you want to go?', options=distr_neight[distr_neight['distritos'].isin(districts)]['neightbour'])
        days = st.selectbox('Which day are you planning to go?', options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], index=5)
        hour = st.selectbox('At what time?', options=hours, index=20)

    st.markdown("<h3>3. Is there any further requirements?</h3>", unsafe_allow_html=True)
    st.markdown("<h10 style='text-align: center'>*Please take into account that excess on filters may end up not finding any restaurant. Just choose those filters you really need.<br>'Maybe' on the options below refers to restaurants that have not specified that parameter.*</h10>", unsafe_allow_html=True)

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



    st.markdown("<h3>4. Please order your data:</h3>", unsafe_allow_html=True)

    limit = st.number_input('How many options do you maximum want?', value=10)
    sorter = st.multiselect('How do you want the output to be sorted?', options=['total_reviews', 'price_level', 'raiting'])
    col1, col2 = st.columns([3, 5])
    with col2:
        submitted = st.form_submit_button("Suggest me restaurants")

col1, col2, col3 = st.columns(3)

with col1:
   st.image("https://www.reasonwhy.es/media/library/supermercado_glovo.png")

with col2:
   st.image("https://www.themarkethink.com/wp-content/uploads/2019/09/toks-uber-eats.jpg")

with col3:  
   st.image("https://www.marketingdirecto.com/wp-content/uploads/2019/05/mcdonalds.jpg")

result = fnc.restaurant_selector(df, raiting=avg_raiting, max_price=price_max, total_reviews=min_reviews,
                       neightbour=neightbours, district=districts, type_of_food=types_of_food, dine_in=dine_in_option, reservable=reservable,
                        serves_beer=beer_option, serves_wine=wine_option, vegetarian=vegeterian_option, takeout=takeout_option,
                        wheelchair_accessible=wheelchair_accessible, day=days, time=hour, sorter=sorter, limit=limit)

df_result = result[['name', 'raiting', 'price_level', 'total_reviews', 'neightbour', 'distritos', 'direction', 'ethnicity']]
df_map = result[['name', 'raiting', 'price_level', 'total_reviews', 'neightbour', 'distritos', 'direction', 'latitud', 'longitud', 'url']]

df_map.to_csv('data/result_cache.csv')
st.markdown("<h3 style='text-align: left'>Restaurants suggested:</h3>", unsafe_allow_html=True)

st.dataframe(df_result)

st.markdown("<a style='text-align: right; color:blue; font-size:26px' href='http://localhost:8501/Map'>Show me on the map!👉</a>", unsafe_allow_html=True)
