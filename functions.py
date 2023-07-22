import numpy as np
import pandas as pd
from datetime import datetime
import time
import os
import sqlalchemy as alch
import requests
from textblob import TextBlob
from nltk import WordNetLemmatizer
import stylecloud
from IPython.display import Image
from nltk.stem import LancasterStemmer
import geopandas as gpd
import folium
import branca.colormap as cm

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

    """Converts a time string in the format 'hh:mmAM' or 'hh:mmPM' to decimal format.

    Args:
        time_string (str): A time string in the format 'hh:mmAM' or 'hh:mmPM', where 'hh' represents hours
                           in 12-hour format (01-12), 'mm' represents minutes (00-59), and 'AM' or 'PM'
                           represents the time period (ante meridiem or post meridiem).

    Returns:
        float: The time in decimal format, calculated as hours + minutes / 60.0.
    """
    time_object = datetime.strptime(time_string, "%I:%M%p")
    hour = time_object.hour
    minute = time_object.minute
    decimal_time = hour + minute / 60.0

    return decimal_time




def spliting_times(my_range):
    """Splits a time range string and returns an array of time values in decimal format.

    The function takes a time range string in the format 'start_time–end_time' and converts both
    the start and end times to decimal format. It handles AM/PM time formats and concatenates the
    time ranges if the end time is earlier than the start time (indicating the range crosses midnight).

    Args:
        my_range (str): A time range string in the format 'start_time–end_time', where 'start_time' and
                        'end_time' are in the format 'hh:mmAM' or 'hh:mmPM'.

    Returns:
        numpy.ndarray: An array of time values in decimal format representing the time range.
    """

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
    """Converts a string containing multiple time ranges to an array of time values in decimal format.

    The function takes a comma-separated string containing multiple time ranges and converts each range to
    an array of time values in decimal format using the `spliting_times` function. If the input 'row' is None,
    the function returns numpy.nan. If the input 'row' is 'Closed', the function returns ['Closed'] to represent
    the business being closed. If there are any issues parsing the input string, the function returns ['Issue'].

    Args:
        row (str): A comma-separated string containing multiple time ranges in the format 'start1–end1, start2–end2, ...'.

    Returns:
        numpy.ndarray: An array of time values in decimal format representing the combined time ranges,
                       or ['Closed'] if the business is closed, or ['Issue'] if there are parsing issues.
    """
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
       

        try: #In case we have >1 time range, such as: 9:00AM-2:00PM, 8PM-11PM. We will be managing the second range here.
            period_2 = row.split(",")[1].strip()
            hours_opened_2 = spliting_times(period_2)
            hours_opened = np.concatenate((hours_opened, hours_opened_2))
        except IndexError:
            pass
        
        try: #Same as above, but in case we have a third range.
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
    """
    Selects and filters restaurants from a DataFrame based on various criteria.

    This function filters a DataFrame containing restaurant data based on user-specified criteria such as minimum rating,
    maximum price level, total reviews count, neighborhood, district, type of food served, dine-in availability,
    reservation availability, beverage services, vegetarian options, takeout availability, wheelchair accessibility,
    operating day, operating hour, and sorting options.

    Args:
        df (pandas.DataFrame): The DataFrame containing restaurant data.
        raiting (float, optional): The minimum rating required for a restaurant to be selected.
        max_price (int, optional): The maximum price level allowed for a restaurant to be selected.
        total_reviews (int, optional): The minimum total reviews count required for a restaurant to be selected.
        neightbour (list, optional): A list of neighborhood names. Only restaurants in these neighborhoods will be selected.
        district (list, optional): A list of district names. Only restaurants in these districts will be selected.
        type_of_food (list, optional): A list of food types. Only restaurants serving these types of food will be selected.
        dine_in (list, optional): A list of options ['Yes', 'No'].
        reservable (list, optional): A list of options ['Yes', 'No']. 
        serves_beer (list, optional): A list of options ['Yes', 'No'].
        serves_wine (list, optional): A list of options ['Yes', 'No'].
        vegetarian (list, optional): A list of options ['Yes', 'No'].
        takeout (list, optional): A list of options ['Yes', 'No']. 
        wheelchair_accessible (list, optional): A list of options ['Yes', 'No'].
        day (str, optional): The operating day. Can be 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', or 'Any'.
        time (str, optional): The operating time in 24-hour format ('hh:mm'). Requires 'day' parameter to be specified.
        sorter (list, optional): A list of sorting options. Can include 'total_reviews', 'raiting', and 'price_level'.
                                 The restaurants will be sorted based on these criteria in the specified order.
                                 By default, sorting is performed in descending order for 'total_reviews' and 'raiting',
                                 and ascending order for 'price_level'.
        limit (int, optional): The maximum number of restaurants to return after filtering and sorting.

    Returns:
        pandas.DataFrame: A DataFrame containing the selected and filtered restaurant data with the specified sorting and limit.
                          If no restaurants meet the specified criteria, an empty DataFrame is returned.
    """

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
    """Extracts and lemmatizes adjectives and verbs from a given text.

    The function takes a text string as input, performs part-of-speech tagging using TextBlob,
    and extracts adjectives and verbs (base and conjugated forms) from the text. It then lemmatizes
    the extracted words using the WordNetLemmatizer to obtain their base form.

    Args:
        text (str): The input text to extract adjectives and verbs from.

    Returns:
        list: A list of lemmatized adjectives and verbs (base forms) found in the text.
    """
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
    """Generates a word cloud of adjectives from the given DataFrame for a specific rating.

    The function filters the DataFrame to select rows with the specified 'raiting' (rating) value.
    It then concatenates all the adjectives from the 'adjectives' column for the selected rows.
    Using the stylecloud library, it generates a word cloud based on the concatenated adjectives,
    and saves the word cloud as an image in the 'Figures' directory with a filename based on the
    rating value.

    Args:
        df (pandas.DataFrame): The DataFrame containing restaurant data, including an 'adjectives'
                               column that holds lists of adjectives for each restaurant.
        raiting (float): The rating value for which the word cloud should be generated.

    Returns:
        PIL.Image.Image: The generated word cloud image as a PIL Image object.
    """
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
    """Identifies related cuisines based on keywords in the input text.

    The function takes a text string as input and identifies related cuisines based on the presence of specific
    keywords associated with each cuisine. It matches the keywords against the input text (case-insensitive)
    and returns a list of cuisines that have keywords present in the text.

    Args:
        text (str): The input text in which the function searches for keywords related to cuisines.

    Returns:
        list: A list of cuisine names that have keywords present in the input text. If no keywords are found,
              an empty list is returned.

    Note:
        The function uses a predefined dictionary `related_dishes` that associates cuisine names with their
        corresponding keywords. Any matching of keywords in the input text with those in the dictionary will
        result in the identification of the respective cuisine.
    """
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
    """Aggregates a list of lists into a single list, removing duplicates.

    The function takes a list of lists as input and aggregates all the elements into a single list,
    removing any duplicate elements in the process.

    Args:
        lst (list): A list of lists, where each sublist contains elements of the same type.

    Returns:
        list: A single list containing all unique elements from the input list of lists.
    """
    return list(set([item for sublist in lst for item in sublist]))

def plot_restaurants(df):
    """Generates an interactive Folium map with restaurant distribution data.

    The function takes a DataFrame containing restaurant data, specifically the column 'distritos' representing
    the districts where each restaurant is located. It groups the restaurants by districts, counts the number
    of restaurants in each district, and generates an interactive Folium map with district boundaries colored
    based on the number of restaurants.

    Args:
        df (pandas.DataFrame): The DataFrame containing restaurant data with a 'distritos' column representing
                               the districts for each restaurant.

    Returns:
        folium.Map: An interactive Folium map displaying the distribution of restaurants in different districts.

    Note:
        The function requires the 'Geojsons/districtes_original.geojson' file to be present. This file contains
        the geographical data (boundaries) of the districts used for plotting on the map."""

    districts = df.groupby('distritos')['place_id'].count()
    districts = pd.DataFrame(districts).reset_index()
    map2 = folium.Map(location=[41.397356, 2.179490], zoom_start=11.4)
    geojson_data_distr = gpd.GeoDataFrame.from_file('Geojsons/districtes_original.geojson')
    to_plot = geojson_data_distr.merge(districts, how='inner', left_on='NOM', right_on='distritos')

    min_count = to_plot['place_id'].min()
    max_count = to_plot['place_id'].max()

# Define the color gradient
    color_map = cm.LinearColormap(
    colors=['#A6C6E4', '#00204C'],  # Dark blue to light blue gradient
    vmin=min_count,
    vmax=max_count
)
    folium.GeoJson(to_plot, style_function=lambda feature: {
        'fillColor': color_map(feature['properties']['place_id']),
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.8
    }).add_to(map2)
    to_plot['centroid'] = to_plot.centroid
    for i in to_plot.index:
            districtes = folium.Marker(location = [to_plot['centroid'][i].y, to_plot['centroid'][i].x], tooltip=str(to_plot['NOM'][i])+"; Total Restaurants: "+ str(to_plot['place_id'][i]))
            districtes.add_to(map2)

    legend_html = '''
        <div style="position: fixed;
                    top: 500px; right: 400px; width: 220px; height: 75px;
                    border:2px solid grey; z-index:9999;
                    background-color: white;
                    font-size:14px;
                    ">
            <p style="margin: 5px; text-align:center;">Legend</p>
            <div style="display: flex; justify-content: space-between; margin: 0 5px;">
                <div style="width: 50px; height: 20px; background-color:#00204C;"></div>
                <div style="width: 50px; height: 20px; background-color:#A6C6E4;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 0 5px;">
                <div style="text-align: center; width: 50px;">Many</div>
                <div style="text-align: center; width: 50px;">Few</div>
            </div>
        </div>
    '''
    map2.get_root().html.add_child(folium.Element(legend_html))
    return map2