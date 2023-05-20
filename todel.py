import folium
import json
import random
import matplotlib.pyplot as plt
import base64
import mpld3
import matplotlib.colors as mcolors
import plotly
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
from pretty_html_table import build_table


def method(data):
    dth = '#ff2e63' 
    rec = '#21bf73'
    act = '#fe9801'
    temp = data[(data["Type local"] != "Dépendance")& (data["Type local"] != "Local industriel. commercial ou assimilé")].reset_index(drop = True)
    temp["Month mutation"] = pd.to_datetime(temp["Date mutation"]).dt.month
    temp['Prix mètre carré 2018'] = temp[pd.to_datetime(temp["Date mutation"]).dt.year == 2018]["Valeur fonciere"]/temp[pd.to_datetime(temp["Date mutation"]).dt.year == 2018]["Surface reelle bati"]
    temp['Prix mètre carré 2019'] = temp[pd.to_datetime(temp["Date mutation"]).dt.year == 2019]["Valeur fonciere"]/temp[pd.to_datetime(temp["Date mutation"]).dt.year == 2019]["Surface reelle bati"]
    temp['Prix mètre carré 2022'] = temp[pd.to_datetime(temp["Date mutation"]).dt.year == 2022]["Valeur fonciere"]/temp[pd.to_datetime(temp["Date mutation"]).dt.year == 2022]["Surface reelle bati"]

    temp =temp.replace(np.inf, np.nan)

    # temp['No. of Recovered to 1 Death Case'] = round(temp['Recovered']/temp['Deaths'], 3)
    temp = temp.groupby('Month mutation')[["Prix mètre carré 2018","Prix mètre carré 2019","Prix mètre carré 2022"]].mean().reset_index()

    temp = temp.melt(id_vars='Month mutation', value_vars=['Prix mètre carré 2018','Prix mètre carré 2019','Prix mètre carré 2022'], 
                    var_name='Departements', value_name='Value')

    fig = px.line(temp, x="Month mutation", y="Value", color='Departements', log_y=True, 
                title='Evolution du prix du mètre carré depuis 2018', color_discrete_sequence=[dth, rec,act])
    retour = plotly.io.to_html(fig)
    fig.show()
    plt.close()


def Heat_map2(data):
    m_2 = data[(data["Type local"] != "Dépendance")& (data["Type local"] != "Local industriel. commercial ou assimilé")].reset_index(drop = True)

    m_2["Prix mètre carré"] = m_2["Valeur fonciere"]/m_2["Surface reelle bati"]

    property_changes = m_2.groupby('Code departement',as_index=False)['Prix mètre carré'].mean()
    print(property_changes.sort_values("Prix mètre carré"))
    property_changes.columns = ['Code', 'property_changes']

    property_dict = property_changes.set_index('Code')['property_changes'].to_dict()

    with open('./data/departements/departements.geojson') as f:
        zone = json.load(f)

    colormap = linear.YlOrRd_09.scale(
        0,
        property_changes.property_changes.max())

    for feature in zone['features']:
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
        zone,
        style_function=style_function,
        name='geojson'
    ).add_to(m)

    colormap.add_to(m)

    print(m._repr_html_())

def heat_map3(data):
    dth = '#ff2e63' 
    rec = '#21bf73'
    cnf  = '#fe9801'
    def location(row):
        if row['Code departement']=='75':
                return 'Paris'
        elif row['Code departement']=='6':
                return 'Alpes-Maritimes'
        elif row['Code departement']=='59':
            return 'Nord'
        else:
            return 'Reste de la France'


    temp = data[(data["Type local"] != "Dépendance")& (data["Type local"] != "Local industriel. commercial ou assimilé")].reset_index(drop = True)
    temp['Prix mètre carré'] = temp['Valeur fonciere']/temp['Surface reelle bati']
    temp['Region'] = temp.apply(location, axis=1)
    temp['Date'] = pd.to_datetime(temp['Date mutation']).dt.strftime('%Y-%m-%d')
    temp = temp.groupby(['Region', 'Date'])['Prix mètre carré'].mean().reset_index()
    temp = temp.melt(id_vars=['Region', 'Date'], value_vars=['Prix mètre carré'], 
                    var_name='Case', value_name='Count').sort_values('Count')
    # temp = temp.sort_values(['Date', 'Region', 'Case']).reset_index()
    temp.head()

    fig = px.bar(temp, y='Region', x='Count', color='Case', barmode='group', orientation='h',
                text='Count', title='Hubei - China - World', animation_frame='Date',
                color_discrete_sequence= [dth, rec, cnf], range_x=[0, 70000])
    fig.update_traces(textposition='outside')
    #fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    fig_html = plotly.io.to_html(fig)
    return HttpResponse(fig_html)

data = pd.read_csv('./data/annee_traitee/2022.csv',sep=',',header=0, low_memory=False)
method(data)