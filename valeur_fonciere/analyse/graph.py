import folium
import json
import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from io import StringIO
import pandas as pd
from colour import Color

def graph_region(zone:str = 'departements',df:pd.DataFrame = None):
    """Génère une carte de France avec les départements ou des regions colorés en fonction du nombre de vente (non propoertionnel)
        param zone : définit quelle données à séléctionner : 'departements' ou 'regions'"""
    geojson_file = f'./data/{zone}.geojson'

    m = folium.Map(location=[46.8566, 2.3522], zoom_start=6)

    with open(geojson_file) as f:
        data = json.load(f)
    if zone == 'regions':
        df['Code postal'] = df['Code postal'].astype(str).str[:2]
    tab = pd.DataFrame(df["Code postal"].value_counts().sort_values(ascending=False))
    red = Color("red")
    #couleurs_hex = list(red.range_to(Color("green"),len(tab)))
    colors = plt.cm.RdYlGn((tab - tab.min()) / (tab.max() - tab.min()))
    couleurs_hex = [mcolors.rgb2hex(c) for c in colors]
    tab['color'] = couleurs_hex
    tab = tab.sort_values(by='Code postal')
    color_dict = {data['features'][i]['properties']['code'] : tab["color"].values[i] for i in range(len(tab["Code postal"]))}
    color_dict.update({data['features'][i]['properties']['code'] : Color("blue").hex for i in range (len(tab["Code postal"]),len(data["features"]))}) # zone where data aren't available

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
def Vente_par_Mois(df:pd.DataFrame) :

    df["Date mutation"] =pd.to_datetime(df['Date mutation'],dayfirst=True).dt.strftime('%d-%m')

    plt.title('Nombre de ventes répartis par mois')
    plt.plot(df["Date mutation"].value_counts()[df['Date mutation'].unique()])
    plt.xticks(rotation=45)
    plt.xlabel('Mois')
    plt.ylabel('Nombre de ventes')

    imgdata = StringIO()
    plt.savefig(imgdata, format='svg')
    return imgdata.getvalue()