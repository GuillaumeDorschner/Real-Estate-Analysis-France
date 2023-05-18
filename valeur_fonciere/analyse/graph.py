import folium
import json
import random
import matplotlib.pyplot as plt
import base64
import matplotlib.colors as mcolors
from io import StringIO
import pandas as pd
from io import BytesIO
from colour import Color
import matplotlib
from django.http import JsonResponse
from django.http import FileResponse
from branca.colormap import linear
from django.http import HttpResponse
matplotlib.use('Agg')

def Vente_par_Mois(request, df):
    df["Date mutation"] =pd.to_datetime(df['Date mutation'],dayfirst=True).dt.strftime('%d-%m')

    plt.title('Nombre de ventes répartis par mois')
    plt.plot(df["Date mutation"].value_counts()[df['Date mutation'].unique()])
    plt.xticks(rotation=45)
    plt.xlabel('Mois')
    plt.ylabel('Nombre de ventes')

    imgdata = io.BytesIO()  # use BytesIO instead of StringIO
    plt.savefig(imgdata, format='svg')
    imgdata.seek(0)  # rewind the data

    svg_data = imgdata.getvalue().decode()

    imgdata.close()  # close the BytesIO object

    return JsonResponse({"graph": svg_data})

def repartionTypeBien(request, df):
    type_counts = df['Type local'].value_counts()
    fig, ax = plt.subplots(figsize=(10,10))
    type_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
    ax.set_ylabel('')
    ax.set_title('Répartition des types de biens')

    buf = BytesIO()
    plt.savefig(buf, format='png')

    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return JsonResponse({"graph": image_base64})

# def data_departement(departement,data):
#     depart = data[(data["Code departement"] == departement) & (data["Type local"] != "Dépendance")& (data["Type local"] != "Local industriel. commercial ou assimilé")].reset_index(drop = True)
#     depart["Prix mètre carré"] = depart["Valeur fonciere"]/depart["Surface reelle bati"]
#     retour = BytesIO
#     pd.table.plotting.table(depart)
#     plt.savefig(retour, format='png')
#     image_base64 = base64.b64encode(retour.getvalue()).decode('utf-8')
#     return JsonResponse({"graph": image_base64})

def top5cher(request, df):
    """top 5 des départements les plus chers"""
    prix_m2_departement = prix_m2(df)
    top5_chers = pd.DataFrame(prix_m2_departement.sort_values(ascending=False).head(5))
    retour = io.BytesIO()  # instantiate BytesIO object

    fig, ax = plt.subplots(figsize=(12, 4))  # Create a new figure with a default 111 subplot
    ax.axis('off')
    pd.plotting.table(ax, top5_chers)  # plot the table

    plt.savefig(retour, format='png')
    plt.close(fig)  # close the figure

    image_base64 = base64.b64encode(retour.getvalue()).decode('utf-8')
    retour.close()  # close the BytesIO object
    return JsonResponse({"graph": image_base64})

def top5moinscher(request, df):
    """top 5 des départements les moins chers"""
    prix_m2_departement = prix_m2(df)
    top5_moins_chers = pd.DataFrame(prix_m2_departement.sort_values(ascending=True).head(5))
    retour = io.BytesIO()  # instantiate BytesIO object

    fig, ax = plt.subplots(figsize=(12, 4))  # Create a new figure with a default 111 subplot
    ax.axis('off')
    pd.plotting.table(ax, top5_moins_chers)  # plot the table

    plt.savefig(retour, format='png')
    plt.close(fig)  # close the figure

    image_base64 = base64.b64encode(retour.getvalue()).decode('utf-8')
    retour.close()  # close the BytesIO object
    return JsonResponse({"graph": image_base64})

def prix_m2(m2):
    """Calcul du prix moyen au m2 par département
    graph non interactif"""
    m2['Valeur fonciere par m2'] = m2['Valeur fonciere'] / m2['Surface terrain']
    prix_m2_departement = m2.groupby('Code departement')['Valeur fonciere par m2'].mean()
    return prix_m2_departement


def heatMap(request, df):

    property_changes = df['Code departement'].value_counts().reset_index()
    property_changes.columns = ['Code', 'property_changes']

    property_dict = property_changes.set_index('Code')['property_changes'].to_dict()

    with open('./data/departements/departements.geojson') as f:
        data = json.load(f)

    colormap = linear.YlOrRd_09.scale(
        property_changes.property_changes.min(),
        property_changes.property_changes.max())

    for feature in data['features']:
        feature['properties']['property_changes'] = property_dict.get(feature['properties']['code'], None)

    def style_function(feature):
        property_changes = feature['properties']['property_changes']
        return {
            'fillOpacity': 0.7,
            'weight': 2,
            'color': 'black',
            'fillColor': '#fff' if property_changes is None else colormap(property_changes)
        }

    m = folium.Map(location=[46.8566, 2.3522], zoom_start=6)

    folium.GeoJson(
        data,
        style_function=style_function,
        name='geojson'
    ).add_to(m)

    colormap.add_to(m)

    return HttpResponse(m._repr_html_())

