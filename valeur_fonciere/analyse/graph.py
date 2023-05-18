import folium
import json
import random
import matplotlib.pyplot as plt
import base64
import mpld3
import matplotlib.colors as mcolors
from io import StringIO
import pandas as pd
import numpy as np
import plotly.subplots as sp
import plotly.graph_objects as go
from io import BytesIO
from colour import Color
import matplotlib
from django.http import JsonResponse
from django.http import FileResponse
from branca.colormap import linear
from django.http import HttpResponse
matplotlib.use('Agg')
import plotly.express as px

def vente_par_mois(request, df):
    """
    Nombre de ventes par mois
    statique
    """
    df["Date mutation"] =pd.to_datetime(df['Date mutation'],dayfirst=True).dt.strftime('%d-%m')
    plt.title('Nombre de ventes répartis par mois')
    plt.plot(df["Date mutation"].value_counts()[df['Date mutation'].unique()])
    plt.xticks(rotation=45)
    plt.xlabel('Mois')
    plt.ylabel('Nombre de ventes')
    html_fig = mpld3.fig_to_html(plt.gcf())
    plt.close()

    return HttpResponse(html_fig)

def repartion_type_bien(request, df):
    plt.cla()
    type_counts = df['Type local'].value_counts()
    fig, ax = plt.subplots(figsize=(10,10))
    type_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
    ax.set_ylabel('')
    ax.set_title('Répartition des types de biens')

    html_fig = mpld3.fig_to_html(fig)
    plt.close(fig)

    return HttpResponse(html_fig)

def top_5_cher(request, df):
    """top 5 des départements les plus chers"""
    prix_m2_departement = prix_m2(df)
    top5_chers = pd.DataFrame(prix_m2_departement.sort_values(ascending=False).head(5))

    fig, ax = plt.subplots(figsize=(12, 4))  # Create a new figure with a default 111 subplot
    ax.axis('off')
    pd.plotting.table(ax, top5_chers)  # plot the table

    html_fig = mpld3.fig_to_html(fig)
    plt.close(fig)  # close the figure

    return HttpResponse(html_fig)

def top_5_moins_cher(request, df):
    """top 5 des départements les moins chers"""
    prix_m2_departement = prix_m2(df)
    top5_moins_chers = pd.DataFrame(prix_m2_departement.sort_values(ascending=True).head(5))

    fig, ax = plt.subplots(figsize=(12, 4))  # Create a new figure with a default 111 subplot
    ax.axis('off')
    pd.plotting.table(ax, top5_moins_chers)  # plot the table

    html_fig = mpld3.fig_to_html(fig)
    plt.close(fig)  # close the figure

    return HttpResponse(html_fig)

def vol_monetaire(df):
    """Volume monétaire par département
    graph fixe"""
    DEPARTMENTS = json.load(open("../data/departements/departements_dict.json")) 
    dict_vol_ventes = df.groupby(["Code departement"])["Valeur fonciere"].sum().reset_index()
    dict_vol_ventes.columns = ["Code departement","Volume monétaire"]
    dict_vol_ventes["Volume monétaire"] = round(dict_vol_ventes["Volume monétaire"]/1000000000,2)
    for i in dict_vol_ventes["Code departement"]:
        dict_vol_ventes.loc[dict_vol_ventes["Code departement"] == i,"Département"] = DEPARTMENTS.get(str(i))
    act = '#fe9801'
    dict_vol_ventes = dict_vol_ventes.sort_values('Code departement', ascending=False)

    fig = px.bar(dict_vol_ventes.sort_values('Volume monétaire', ascending=False).head(10).sort_values('Volume monétaire', ascending=True), 
                x="Volume monétaire", y="Département", text='Volume monétaire', orientation='h', 
                width=700, height=600, range_x = [0, 500], title='Volume monétaire par département en Milliards')
    fig.update_traces(marker_color=act, opacity=0.8, textposition='outside')
    image_html = fig.to_html()
    return JsonResponse({"Vol_monetaire": image_html})

def prix_m2(m2):
    """Calcul du prix moyen au m2 par département
    graph non interactif"""
    df['Valeur fonciere par m2'] = df['Valeur fonciere'] / df['Surface terrain']
    prix_m2_departement = df.groupby('Code departement')['Valeur fonciere par m2'].mean()
    return prix_m2_departement

    prix_metre_carre["Prix mètre carré"] = prix_metre_carre["Valeur fonciere"]/prix_metre_carre["Surface reelle bati"]
    return prix_metre_carre

def heat_map(request, df):

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

def nb_ventes(request, df):
    """Nombre de ventes par département
    graph fixe"""
    dict_nb_ventes = pd.DataFrame(df["Code departement"].value_counts()).reset_index()
    dict_nb_ventes.columns = ["Code departement", "Nombre de ventes"]
    for i in dict_nb_ventes["Code departement"]:
        dict_nb_ventes.loc[dict_nb_ventes["Code departement"] == i, "Département"] = DEPARTMENTS.get(str(i))

    act = '#fe9801'
    temp = dict_nb_ventes
    temp = temp.sort_values('Code departement', ascending=False)

    fig = sp.make_subplots(rows=1, cols=2, subplot_titles=['Top 5 par départements les plus vendeurs', 'Top 5 par départements les moins vendeurs'])

    fig.add_trace(go.Bar(x=temp.sort_values('Nombre de ventes', ascending=False).head(5).sort_values('Nombre de ventes', ascending=True)["Nombre de ventes"],
                        y=temp.sort_values('Nombre de ventes', ascending=False).head(5).sort_values('Nombre de ventes', ascending=True)["Département"],
                        text=temp.sort_values('Nombre de ventes', ascending=False).head(5).sort_values('Nombre de ventes', ascending=True)["Nombre de ventes"],
                        textposition='outside',
                        marker_color=act,
                        opacity=0.8,
                        orientation='h'),
                row=1, col=1)

    fig.add_trace(go.Bar(x=temp.sort_values('Nombre de ventes', ascending=False).tail(5).sort_values('Nombre de ventes', ascending=False)["Nombre de ventes"],
                        y=temp.sort_values('Nombre de ventes', ascending=False).tail(5).sort_values('Nombre de ventes', ascending=False)["Département"],
                        text=temp.sort_values('Nombre de ventes', ascending=False).tail(5).sort_values('Nombre de ventes', ascending=False)["Nombre de ventes"],
                        textposition='outside',
                        marker_color=act,
                        opacity=0.8,
                        orientation='h'),
                row=1, col=2)

    fig.update_layout(showlegend=False)

    fig.update_xaxes(range=[50000, 110000], row=1, col=1)

    fig.update_xaxes(range=[1000, 4000], row=1, col=2)
    
    fig_html = fig.to_html()
    return JsonResponse({"nb_ventes": fig_html})

