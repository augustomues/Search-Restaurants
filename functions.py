import datetime
import numpy as np
import pandas as pd
from datetime import datetime
import time
import seaborn as sns
import matplotlib as plt
import os
import sqlalchemy as alch
import requests
from textblob import TextBlob
from nltk import WordNetLemmatizer
import stylecloud
from IPython.display import Image
from nltk.stem import LancasterStemmer

#SCRAPPING FUNCTIONS
payload={}
headers = {}
def norm_req(i, radius, API_KEY, total_req):
    """
    Sends a normalized request to the Google Places API to search for nearby restaurants based on the provided location and radius.

    Args:
        i (str): The location coordinates in the format "latitude%2Clongitude".
        radius (int): The radius (in meters) within which to search for restaurants.
        API_KEY (str): The API key to access the Google Places API.
        total_req (int): The total number of requests made so far.

    Returns:
        requests.Response: The response object containing the result of the API request.
    """
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={i}&radius={radius}&type=restaurantes&keyword=restaurant&key={API_KEY}"
    response = requests.request("GET", url, headers=headers, data=payload)
    total_req += 1
    return response

def next_page_req(response, APY_KEY, total_req):
    """
    Sends a request to the Google Places API to retrieve the next page of results based on the provided response object. The previous request
    can return up to 60 results, organized in 3 pages with 20 results each. If that is the case, the previous request will contain the argument
    'next_page_toke'. If not, this argument will not be on the resposne

    Args:
        response (requests.Response): The response object from the previous API request.
        API_KEY (str): The API key to access the Google Places API.
        total_req (int): The total number of requests made so far.

    Returns:
        requests.Response: The response object containing the result of the API request for the next page.
    """
    time.sleep(5)
    next_page = response.json()['next_page_token']
    url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={next_page}&key={APY_KEY}'
    response = requests.request("GET", url, headers=headers, data=payload)
    total_req += 1
    return response

def appending_responses(response, business_type, location, name, place_id, raiting, price_level, user_raitings_total, vicinity):
    """
    Extracts specific information from the response object and appends it to the corresponding lists.

    Args:
        response (requests.Response): The response object from the API request.
        business_type (list): The list to store the business status of each result.
        location (list): The list to store the location of each result.
        name (list): The list to store the name of each result.
        place_id (list): The list to store the place ID of each result.
        rating (list): The list to store the rating of each result.
        price_level (list): The list to store the price level of each result.
        user_ratings_total (list): The list to store the total number of user ratings for each result.
        vicinity (list): The list to store the vicinity (address or neighborhood) of each result.

    Returns:
        tuple: A tuple containing the updated lists of business_type, location, name, place_id, rating,
               price_level, user_ratings_total, and vicinity.
    """
    for i in response.json()['results']:
        try:
            business_type.append(i['business_status'])
        except KeyError:
            business_type.append(np.nan)
        try:
            location.append(i['geometry']['location'])
        except KeyError:
            location.append(np.nan)
        try:
            name.append(i['name'])
        except KeyError:
            name.append(np.nan)
        try:
            place_id.append(i['place_id'])
        except KeyError:
            place_id.append(np.nan)
        try:
            raiting.append(i['rating'])
        except KeyError:
            raiting.append(np.nan)
        try:
            price_level.append(i['price_level'])
        except KeyError:
            price_level.append(np.nan)
        try:
            user_raitings_total.append(i['user_ratings_total'])
        except KeyError:
            user_raitings_total.append(np.nan)
        try:
            vicinity.append(i['vicinity'])
        except:
            vicinity.append(np.nan)
    return business_type, location, name, place_id, raiting, price_level, user_raitings_total, vicinity

def get_barrios(df, long, lat):
    """
    Retrieves the name of the neighborhood (barrio) that intersects with the specified coordinates.

    Parameters:
    - lat (float): Latitude of the location.
    - long (float): Longitude of the location.

    Returns:
    - str: The name of the neighborhood (barrio) that intersects with the specified coordinates.
           If no intersection is found, it returns "Not found".
    """
    my_position = {"type": "Point", "coordinates": [long, lat]} # o al revés

    result = df.find_one(
            {"geometry": 
                    {"$geoIntersects": 
                        {"$geometry": my_position}}
            })
    try:
        return result["properties"]["NOM"]
    except:
        return "Not found"



def create_connection(schema):
    """
    Creates a connection to a MySQL database using the provided schema, table name, and DataFrame.

    Args:
        schema (str): The name of the database schema.
        table_name (str): The name of the table to connect to.
        df (pandas.DataFrame): The DataFrame containing the data to be inserted into the table.

    Returns:
        sqlalchemy.engine.Engine: The engine object representing the database connection.
    """
    dbName = schema
    password = os.getenv('workbench_pass')
    connectionData=f"mysql+pymysql://root:{password}@localhost/{dbName}"
    engine = alch.create_engine(connectionData)
    return engine

def upload_data_bulky(df, table_name, schema):
    """
    Uploads a DataFrame to a SQL database table using the specified schema.

    Parameters:
        df (pandas.DataFrame): The DataFrame to be uploaded.
        table_name (str): The name of the table in the database.
        schema (str): The schema of the database connection.

    Returns:
        None
    """

    df.to_sql(con=create_connection(schema), name=table_name, if_exists='replace')



def convert_time_to_decimal(time_string):
    time_object = datetime.strptime(time_string, "%I:%M%p")
    hour = time_object.hour
    minute = time_object.minute
    decimal_time = hour + minute / 60.0

    return decimal_time




def spliting_times(my_range):
    period_start = my_range.split('–')[0]
    period_finish = my_range.split('–')[1]
    if period_start[-2:] == 'AM' or period_start[-2:] == 'PM':
        pass
    else:
        period_start += period_finish[-2:]
 
    period_start = convert_time_to_decimal(period_start)
    period_finish = convert_time_to_decimal(period_finish)

    if period_start > period_finish:
        range1 = np.arange(period_start, 24, 0.25)
        range2 = np.arange(0, period_finish, 0.25)
        range = np.concatenate((range1, range2))
    else:
        range = np.arange(period_start, period_finish, 0.25)
    return range




def converting_times_to_ranges(row):
    if row == None:
        return np.nan

    elif row == 'Closed':
        return ['Closed']
    
    else:
        try:
            period_1 = row.split(",")[0].strip()
            hours_opened = spliting_times(period_1)
        except:
            return ['Issue']
       

        try:
            period_2 = row.split(",")[1].strip()
            hours_opened_2 = spliting_times(period_2)
            hours_opened = np.concatenate((hours_opened, hours_opened_2))
        except IndexError:
            pass
        
        try:
            period_3 = row.split(",")[2].strip()
            hours_opened_3 = spliting_times(period_3)
            hours_opened = np.concatenate((hours_opened, hours_opened_3))
        except IndexError:
            pass

        return hours_opened




def restaurant_selector(df, raiting=None, max_price=None, total_reviews=None,
                       neightbour=None, district=None, type_of_food=None, dine_in=['Yes'], reservable=None,
                        serves_beer=None, serves_wine=None, vegetarian=None, takeout=None,
                        wheelchair_accessible=None, day='Any', time=None, sorter=None, limit=10):

    days = {'Monday': 'mon_hours'
            ,'Tuesday': 'tue_hours'
            ,'Wednesday': 'wed_hours'
            ,'Thursday': 'tue_hours'
            ,'Friday': 'fri_hours'
            ,'Saturday': 'sat_hours'
            ,'Sunday': 'sun_hours'}
    
    sorter_ord = {'total_reviews': False
            , 'raiting': False
            , 'price_level': True}

    if raiting:
        df = df[df['raiting'] >= raiting]
    if max_price:
        df = df[df['price_level'] <= max_price]
    if total_reviews:
        df = df[df['total_reviews'] >= total_reviews]
    if neightbour:
        df = df[df['neightbour'].isin(neightbour)]
    if district:
        df = df[df['distritos'].isin(district)]
    if dine_in:
        df = df[df['dine_in'].isin(dine_in)]
    if reservable:
        df = df[df['reservable'].isin(reservable)]
    if serves_beer:
        df = df[df['serves_beer'].isin(serves_beer)]
    if serves_wine:
        df = df[df['serves_wine'].isin(serves_wine)]
    if vegetarian:
        df = df[df['vegeterian'].isin(vegetarian)]
    if takeout:
        df = df[df['takeout'].isin(takeout)]
    if wheelchair_accessible:
        df = df[df['wheel_chair_acc'].isin(wheelchair_accessible)]
    if day != 'Any':
        hours_column = days[day]
        df = df[df[hours_column].apply(lambda x: x != ['Closed'] if isinstance(x, list) else True)]
    if time:
        if day == 'Any':
            raise KeyError('Invalid hour. If an hour is passed, a day must be passed as well')
        else:
            df = df[df.apply(lambda row: isinstance(row[days[day]], np.ndarray) and time in row[days[day]] if day and days.get(day) else False, axis=1)]
    if type_of_food:
        df = df.dropna(subset=['ethnicity'])
        df = df[df['ethnicity'].apply(lambda x: type_of_food[0] in x)]
    try:
        sort_asc = []
        for i in sorter:
            sort_asc.append(sorter_ord[i])
        df = df.sort_values(by=sorter, ascending=sort_asc)
    except:
        pass

    return df.head(limit).reset_index(drop=True)

def get_words(text):
    lemmatizer = WordNetLemmatizer()
    my_list = []
    blob = TextBlob(str(text))
    list =  [ word for (word,tag) in blob.tags if tag in ["JJ", "JJR", "JJS", "VB", "VBD", "VBG", "VBN", "VBP", "VBP", "VBZ"]]
    for i in list:
        i = lemmatizer.lemmatize(i)
        if i == "wa":
            pass
        else:
            if i in my_list:
                pass
            else:
                my_list.append(i)
    return my_list

def word_cloud(df, raiting):
    my_str = ''
    for i in df[(df['reviews_rating'] == raiting)]['adjectives']:
        for j in i:
            my_str += " " + j
    
    stylecloud.gen_stylecloud(text=my_str,
                            icon_name='fas fa-utensils',
                            palette ='cmocean.sequential.Haline_17',
                            background_color='white',
                            output_name=f'Figures/2. words_{raiting}.png')
    return Image(filename=f'Figures/2. words_{raiting}.png')

def get_food(text):
    related_dishes = {
    'Italian': ['Italy', 'Italian', 'Pasta', 'Pizza', 'Carbonara', 'Lasagna', 'Tiramisu'],
    'Japanese': ['Japan', 'Japanese', 'Sushi', 'Ramen', 'Tempura', 'Sashimi', 'Matcha'],
    'Mexican': ['Mexico', 'Mexican', 'Tacos', 'Guacamole', 'Enchiladas', 'Chiles Rellenos', 'Mole'],
    'Indian': ['India', 'Indian', 'Curry', 'Naan', 'Biryani', 'Tandoori', 'Gulab Jamun'],
    'Spanish': ['Spain', 'Spanish', 'Paella', 'Tapas', 'Sangria', 'Gazpacho', 'Churros'],
    'Korean': ['Korea', 'Korean', 'Kimchi', 'Bulgogi', 'Bibimbap', 'Korean BBQ', 'Japchae'],
    'Thai': ['Thailand', 'Thai', 'Pad Thai', 'Tom Yum', 'Green Curry', 'Mango Sticky Rice', 'Som Tum'],
    'Peruvian': ['Peru', 'Peruvian', 'Ceviche', 'Lomo Saltado', 'Aji de Gallina', 'Anticuchos', 'Pisco Sour'],
    'Chinese': ['China', 'Chinese', 'Dim Sum', 'Peking Duck', 'Kung Pao Chicken', 'Hot Pot', 'Mapo Tofu'],
    'Greek': ['Greece', 'Greek', 'Moussaka', 'Souvlaki', 'Tzatziki', 'Dolmades', 'Baklava'],
    'French': ['France', 'French', 'Croissant', 'Escargot', 'Coq au Vin', 'Ratatouille', 'Crème Brûlée'],
    'Argentinian/Uruguayan': ['Argentina', 'Argentinian', 'Uruguay', 'Uruguayan', 'Empanada', 'Asado', 'Milanesa', 'Escalope'],
    'Burger': ['Burger', 'Hamburger', 'Smash']
}
    # Convert the text to lowercase for case-insensitive matching
    try:
        text_lower = text.lower()
    except AttributeError:
        return []
    
    # Initialize an empty list to store the matching keys
    matching_keys = []
    stemmer = LancasterStemmer()
    stemmed_text = stemmer.stem(text_lower)
    # Iterate over the key-value pairs in the dictionary
    for key, values in related_dishes.items():
        # Check if any of the values are present in the text
        for value in values:
            if value.lower() in text_lower or value.lower() in stemmed_text:
                matching_keys.append(key)
                break  # Break out of the inner loop if a match is found
        
    return matching_keys

def aggregate_ethnicity(lst):
    return list(set([item for sublist in lst for item in sublist]))


def count_places_distr(df, rating):
   df = df[df['raiting'] >= rating]
   y = df.groupby(by='distritos')['place_id'].count().sort_values(ascending=False)
   sns.barplot(x=y.index, y=y.values)
   plt.xticks(rotation=45)
   plt.xlabel('Districts')
   plt.ylabel('Total Restaurants')
   plt.title('Total Restaurants by districts')

def count_places_barrios(df, district, rating):
   df = df[(df['raiting'] >= rating) & (df['distritos'] == district)]
   y = df.groupby(by='neightbour')['place_id'].count().sort_values(ascending=False)
   sns.barplot(x=y.index, y=y.values)
   plt.xticks(rotation=90)
   plt.xlabel('Neightbours')
   plt.ylabel('Total Restaurants')
   plt.title('Total Restaurants by neightbours');