import datetime
import numpy as np
import pandas as pd
from datetime import datetime
import time




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
                       neightbour=None, district=None, dine_in=['Yes'], reservable=None,
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
        df = df[df['wheelchair_accessible'].isin(wheelchair_accessible)]
    if day != 'Any':
        hours_column = days[day]
        df = df[df[hours_column].apply(lambda x: x != ['Closed'] if isinstance(x, list) else True)]
    if time:
        if day == 'Any':
            raise KeyError('Invalid hour. If an hour is passed, a day must be passed as well')
        else:
            df = df[df.apply(lambda row: isinstance(row[days[day]], np.ndarray) and time in row[days[day]] if day and days.get(day) else False, axis=1)]
    try:
        sort_asc = []
        for i in sorter:
            sort_asc.append(sorter_ord[i])
        df = df.sort_values(by=sorter, ascending=sort_asc)
    except:
        pass

    return df[['name', 'direction', 'raiting', 'price_level', 'total_reviews', 'neightbour', 'distritos', 'latitud', 'longitud']].head(limit).reset_index(drop=True)