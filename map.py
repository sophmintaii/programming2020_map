from geopy.extra.rate_limiter import RateLimiter
import folium
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
geolocator = Nominatim(user_agent="specify_your_app_name_here", timeout=100)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.01)


def get_data_dict(path, inp_year):
    '''
    str, int -> dict{str: list[str]}
    Returns dict where each item is location: list of titles to be filmed here
    '''
    data = pd.read_csv(path, error_bad_lines=False, warn_bad_lines=False)
    movies = data['movie']
    years = data['year']
    locations = data['location']
    data_dict = {}
    counter = 0
    for movie, year, location in zip(movies, years, locations):
        try:
            year = int(year)
            if year == inp_year and counter < 500:
                if location not in data_dict:
                    data_dict[location] = [movie]
                else:
                    data_dict[location].append(movie)
                counter += 1
        except:
            pass
    return data_dict


def change_name(name):
    '''
    str -> str
    returns changed name of the location
    '''
    if 'New York' in name:
        return 'New York USA'
    if 'Los Angeles' in name:
        return 'Los Angeles USA'
    if 'Rio de Janeiro' in name:
        return 'Rio de Janeiro Brazil'
    return ' '.join(name.split(' ')[-2:])


def sort_locations(input_loc, data):
    '''
    tuple, dict{str: list[str]} -> dict{tuple: list[str]}
    returns elements of the data sorted based on
    the distance to the user's location
    '''
    coord_data = dict()
    input_loc = tuple(input_loc)
    for place in data:
        geolocator = Nominatim(user_agent='specify_your_app_name_here')
        try:
            location = geolocator.geocode(place)
            coord = (location.latitude, location.longitude)
            coord_data[coord] = data[place]
        except:
            try:
                place = change_name(place)
                location = geolocator.geocode(place)
                coord = (location.latitude, location.longitude)
                coord_data[coord] = data[place]
            except:
                pass
    coords_sorted = list(coord_data.keys())
    coords_sorted.sort(
        key=lambda x: geodesic(input_loc, x))
    res_data = dict()
    counter = 0
    top = 10 if len(coords_sorted) >= 10 else len(coords_sorted)
    for coord in coords_sorted:
        if counter < top:
            try:
                res_data[coord] = coord_data[coord]
                counter += 1
            except:
                pass
        else:
            return res_data


def get_map_of_numbers(places, curr_loc):
    '''
    dict{tuple: list[str]}, tuple -> folium map
    Returns a layer for the map which displays
    a map with tagged locations and number of movies
    filmed there
    '''
    film = folium.FeatureGroup(name='Films')

    for place in places:
        num = len(places[place])
        folium.Marker(
            location=list(place),
            popup='\n'.join(places[place]),
            icon=folium.Icon(icon='film'),
            tooltip=str(num) + 'films\n(click me!)'
        ).add_to(film)
    return film


def get_area_map(geojson, curr_loc):
    '''
    str, tuple -> folium map
    returns a new layer for the map which displays countries' area
    '''
    area = folium.FeatureGroup(name='Area')
    area.add_child(folium.GeoJson(
        data=open(geojson, 'r',
                  encoding='utf-8-sig').read(),
        style_function=lambda x: {'fillColor': '#c0ffb3'
                                  if x['properties']['AREA'] < 30000
                                  else '#52de97' if (
                                      30000 <= x['properties']['AREA'] and
                                      x['properties']['AREA'] < 100000)
                                  else '#3c9d9b' if (
                                      100000 <= x['properties']['AREA'] and
                                      x['properties']['AREA'] < 600000)
                                  else '#394a6d',
                                  'color': '#1d4d4f',
                                  'fillOpacity': 0.9}))
    return area


def main(inp_year, loc):
    '''
    int, tuple -> follium map
    saves follium map with film markers and area info to the file
    '''
    map = folium.Map(location=loc,
                     zoom_start=7)
    data = get_data_dict('map/locations.csv', inp_year)
    data = sort_locations(loc, data)
    map.add_child(get_map_of_numbers(data, loc))
    map.add_child(get_area_map('map/world.json', loc))
    map.add_child(folium.LayerControl())
    map.save('map/test.html')


if __name__ == '__main__':
    inp_year = input('Type year you want to get information for: ')
    while not inp_year.isdigit():
        inp_year = input('Type year you want to get information for: ')
    inp_year = int(inp_year)

    while True:
        try:
            lat = float(input('Type your latitude: '))
            break
        except TypeError:
            continue

    while True:
        try:
            lon = float(input('Type your longitude: '))
            break
        except TypeError:
            continue

    main(inp_year, tuple((lat, lon)))
