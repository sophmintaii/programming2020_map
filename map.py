import folium
import pandas as pd
from geopy.geocoders import Nominatim


def get_data_dict(path):
    '''
    str -> dict{int: list[str, str]}
    Returns dict where each item is year: list of [location, title]
    '''
    data = pd.read_csv(path)
    movies = data['movie']
    years = data['year']
    locations = data['location']
    data_dict = {}
    for movie, year, location in zip(movies, years, locations):
        try:
            year = int(year)
            if year not in data_dict:
                data_dict[year] = [[location, movie]]
            else:
                data_dict[year].append([location, movie])
        except:
            pass
    return data_dict


def get_titles(data):
    '''
    list[str, str] -> dict{str: list[str]}
    Returns a dictionary where each item is location: list of movies filmed there
    '''
    res = dict()
    for item in data:
        if item[0] not in res:
            res[item[0]] = [item[1]]
        else:
            res[item[0]].append(item[1])
    return res
        

def get_color(number):
    '''
    int -> str
    Returns corresponding to number color of icon etc.
    '''
    if number <= 5:
        return 'green'
    if number <= 10:
        return 'yellow'
    if number <= 20:
        return 'orange'
    return 'red'


def get_map_of_numbers(places, curr_loc):
    '''
    dict{str: list[str]} -> folium map
    Returns a layer for the map which displays a map with tagged locations and number of movies filmed there
    '''
    m = folium.Map(
        location = curr_loc,
        zoom_start=17
    )
    for place in places:
        geolocator = Nominatim(user_agent='specify_your_app_name_here')
        location = geolocator.geocode(place)
        coord = [location.latitude, location.longitude]
        num = len(places[place])
        folium.Marker(
            location=coord,
            popup=num,
            icon=folium.Icon(color=get_color(num))
        ).add_to(m)
    return m


def main():
    loc = [48.314775, 25.082925]
    map = folium.Map(location=loc)
    data = get_data_dict('/home/smint/Documents/sem2/labs/lab2/map/test.csv')
    titles = get_titles(data[2010])

    map.add_child(get_map_of_numbers(titles, loc))
    map.save('test.html')


main()
# data = get_data_dict('/home/smint/Documents/sem2/labs/lab2/map/test.csv')
# #print(data)
# print(get_titles(data[2015]))
# #read_file('/home/smint/Documents/sem2/labs/lab2/map/test.csv')
