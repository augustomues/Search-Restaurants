import pandas as pd
import functions as fnc
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

st.set_page_config(page_title="Let's eat", page_icon='🍽️', layout='wide', initial_sidebar_state='expanded')


image = Image.open('Logo.png')

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.image(image, width=500)

st.markdown("<h3 style='text-align: center'>Let's explore a little bit the data!</h3>", unsafe_allow_html=True)
st.markdown("<p>Below we can see the total restaurants we can find in each district</p>", unsafe_allow_html=True)
df_1 = pd.read_csv('data/barc_restaurants.csv')
df_2 = pd.read_csv('data/place_details.csv')
df_3 = pd.read_csv('data/restaurants_urls.csv')
for i in df_2.columns[9:]:
    df_2[i] = df_2[i].apply(lambda x: fnc.converting_times_to_ranges(x))
df_m_1 = df_1.merge(df_2, how='inner', on='place_id')
df = df_m_1.merge(df_3, how='inner', on='place_id')
df = df[df['distritos'] != 'Not found']

fig = plt.figure(figsize=(10, 4))
y = df.groupby(by='distritos')['place_id'].count().sort_values(ascending=False)
sns.barplot(x=y.index, y=y.values)
plt.xticks(rotation=45)
plt.xlabel('Districts')
plt.ylabel('Total Restaurants')
plt.title('Total Restaurants by districts')
st.pyplot(fig)

st.markdown("<p></p>", unsafe_allow_html=True)
fig = plt.figure(figsize=(10, 4))
df = df[df['raiting'] >= 4]
y = df.groupby(by='distritos')['place_id'].count().sort_values(ascending=False)
sns.barplot(x=y.index, y=y.values)
plt.xticks(rotation=45)
plt.xlabel('Districts')
plt.ylabel('Total Restaurants')
plt.title('Total Restaurants by districts')
st.pyplot(fig)