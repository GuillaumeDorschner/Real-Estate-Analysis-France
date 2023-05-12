import folium
import json
import random

def graph():
    geojson_file = './data/departements.geojson'

    print(geojson_file)

    m = folium.Map(location=[46.8566, 2.3522], zoom_start=6)

    with open(geojson_file) as f:
        data = json.load(f)

    colors = ['#'+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(len(data['features']))]

    color_dict = {data['features'][i]['properties']['code']: colors[i] for i in range(len(data['features']))}

    def style_function(feature):
        return {
            'fillColor': color_dict[feature['properties']['code']],
            'fillOpacity': 0.7,
            'weight': 2,
            'color': 'black'
        }

    folium.GeoJson(
        data,
        style_function=style_function,
        name='geojson'
    ).add_to(m)

    m = m._repr_html_()

    return m