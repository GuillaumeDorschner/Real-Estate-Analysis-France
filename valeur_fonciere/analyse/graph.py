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

def vol_monetaire(request,df):
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

def prix_m2(request,df):
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

def evo_m2(request,data):
    temp = data[(data["Type local"] != "Dépendance")& (data["Type local"] != "Local industriel. commercial ou assimilé")].reset_index(drop = True)
    temp["Month mutation"] = temp["Date mutation"].dt.month

    temp['Prix mètre carré Paris 2018'] = temp[(temp["Code departement"] == '75')&(temp["Date mutation"].dt.year == 2018)]["Valeur fonciere"]/temp[(temp["Code departement"] == '75')&(temp["Date mutation"].dt.year == 2018)]["Surface reelle bati"]
    temp['Prix mètre carré Paris 2019'] = temp[(temp["Code departement"] == '75')&(temp["Date mutation"].dt.year == 2019)]["Valeur fonciere"]/temp[(temp["Code departement"] == '75')&(temp["Date mutation"].dt.year == 2019)]["Surface reelle bati"]
    temp['Prix mètre carré Paris 2022'] = temp[(temp["Code departement"] == '75')&(temp["Date mutation"].dt.year == 2022)]["Valeur fonciere"]/temp[(temp["Code departement"] == '75')&(temp["Date mutation"].dt.year == 2022)]["Surface reelle bati"]

    temp =temp.replace(np.inf, np.nan)

    # temp['No. of Recovered to 1 Death Case'] = round(temp['Recovered']/temp['Deaths'], 3)
    temp = temp.groupby('Month mutation')["Prix mètre carré Paris 2018","Prix mètre carré Paris 2019","Prix mètre carré Paris 2022"].mean().reset_index()

    temp = temp.melt(id_vars='Month mutation', value_vars=['Prix mètre carré Paris 2018','Prix mètre carré Paris 2019','Prix mètre carré Paris 2022'], 
                    var_name='Departements', value_name='Value')

    fig = px.line(temp, x="Month mutation", y="Value", color='Departements', log_y=True, 
                title='Evolution du prix du mètre carré à paris depuis 2018', color_discrete_sequence=[dth, rec,act])
    retour = mpld3.fig_to_html(plt.gcf())
    plt.close()
    return HttpResponse(retour)

def nb_ventes_par_mois(request, data):
    """Nombre de ventes par mois
    graph fixe"""
    df = pd.DataFrame(data)
    df["Date mutation"] =pd.to_datetime(df['Date mutation'],dayfirst=True).dt.strftime('%y-%m')
    plt.figure(figsize=(20,10))
    plt.title('Nombre de ventes répartis par mois')
    plt.plot(df["Date mutation"].value_counts()[df['Date mutation'].unique()])
    plt.xticks(rotation=45)
    plt.xlabel('Date')
    plt.ylabel('Nombre de ventes')
    plt.show()
    html_fig = mpld3.fig_to_html(plt.gcf())
    plt.close()
    return HttpResponse(html_fig)

def evo_m_Carrez (request,df):
    dth = '#ff2e63' 
    rec = '#21bf73'
    act = '#fe9801'
    temp = df[(df["Type local"] != "Dépendance")& (df["Type local"] != "Local industriel. commercial ou assimilé")].reset_index(drop = True)
    temp["Month mutation"] = temp["Date mutation"].dt.month
    temp["carrez_sum"] = temp["Surface Carrez du 1er lot"].fillna(0)  +  temp["Surface Carrez du 2eme lot"].fillna(0) + temp["Surface Carrez du 3eme lot"].fillna(0) + temp["Surface Carrez du 4eme lot"].fillna(0) + temp["Surface Carrez du 5eme lot"].fillna(0)
    temp["Prix mètre carré"] = np.where(temp["carrez_sum"] != 0,temp["Valeur fonciere"]/temp["carrez_sum"],temp["Valeur fonciere"]/temp["Surface reelle bati"])
    temp = temp.drop(np.where(temp['Prix mètre carré'] > 25000)[0])

    temp['Prix mètre carré Paris 2018'] = temp[(temp["Code departement"] == '75')&(temp["Date mutation"].dt.year == 2018)]["Prix mètre carré"]
    temp['Prix mètre carré Paris 2019'] = temp[(temp["Code departement"] == '75')&(temp["Date mutation"].dt.year == 2019)]["Prix mètre carré"]
    temp['Prix mètre carré Paris 2022'] = temp[(temp["Code departement"] == '75')&(temp["Date mutation"].dt.year == 2022)]["Prix mètre carré"]

    temp =temp.replace(np.inf, np.nan)

    # temp['No. of Recovered to 1 Death Case'] = round(temp['Recovered']/temp['Deaths'], 3)
    temp = temp.groupby('Month mutation')["Prix mètre carré Paris 2018","Prix mètre carré Paris 2019","Prix mètre carré Paris 2022"].mean().reset_index()

    temp = temp.melt(id_vars='Month mutation', value_vars=['Prix mètre carré Paris 2018','Prix mètre carré Paris 2019','Prix mètre carré Paris 2022'], 
                    var_name='Departements', value_name='Value')

    fig = px.line(temp, x="Month mutation", y="Value", color='Departements', log_y=True, 
                title='Evolution du prix du mètre carré à paris depuis 2018', color_discrete_sequence=[dth, rec,act])
    fig_html = mpld3.fig_to_html(plt.gcf())
    return HttpResponse(fig_html)

def location(row):
        if row['Code departement']=='75':
                return 'Paris'
        elif row['Code departement']=='6':
                return 'Alpes-Maritimes'
        elif row['Code departement']=='59':
            return 'Nord'
        else:
            return 'Reste de la France'
        

def graph_dynamique1(request,data):
    dth = '#ff2e63' 
    rec = '#21bf73'
    carrez = data[(data["Type local"] != "Dépendance")& (data["Type local"] != "Local industriel. commercial ou assimilé")].reset_index(drop = True)
    carrez["carrez_sum"] = data["Surface Carrez du 1er lot"].fillna(0)  +  data["Surface Carrez du 2eme lot"].fillna(0) + data["Surface Carrez du 3eme lot"].fillna(0) + data["Surface Carrez du 4eme lot"].fillna(0) + data["Surface Carrez du 5eme lot"].fillna(0)
    carrez["Prix mètre carré"] = np.where(carrez["carrez_sum"] != 0,carrez["Valeur fonciere"]/carrez["carrez_sum"],carrez["Valeur fonciere"]/carrez["Surface reelle bati"])
    carrez = carrez.drop(np.where(carrez['Prix mètre carré'] > 25000)[0])

    


    temp = carrez.copy()
    temp['Region'] = temp.apply(location, axis=1)
    temp['Date'] = temp['Date mutation'].dt.strftime('%Y-%m-%d')
    temp = temp.groupby(['Region', 'Date'])['Prix mètre carré'].mean().reset_index()
    temp = temp.melt(id_vars=['Region', 'Date'], value_vars=['Prix mètre carré'], 
                    var_name='Case', value_name='Count').sort_values('Count')
    # temp = temp.sort_values(['Date', 'Region', 'Case']).reset_index()
    temp.head()

    fig = px.bar(temp, y='Region', x='Count', color='Case', barmode='group', orientation='h',
                text='Count', title='Hubei - China - World', animation_frame='Date',
                color_discrete_sequence= [dth, rec, cnf], range_x=[0, 15000])
    fig.update_traces(textposition='outside')
    # fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    # fig.update_layout(yaxis={'categoryorder':'array', 
    #                          'categoryarray':['Hubei','Other Chinese Provinces','Rest of the World']})
    fig_html = mpld3.fig_to_html(plt.gcf())
    return HttpResponse(fig_html)

def graoh_dynamique2(request,carrez):
    cnf = '#393e46'
    temp = carrez.copy()
    temp['Region'] = temp.apply(location, axis=1)
    temp = temp.groupby('Region')['Prix mètre carré'].mean().reset_index()
    temp = temp.melt(id_vars='Region', value_vars=['Prix mètre carré'], 
                    var_name='Case', value_name='Count').sort_values('Count')
    temp.head()

    fig = px.bar(temp, y='Region', x='Count', color='Case', barmode='group', orientation='h',
                text='Count', title='Paris - Nord - Alpes-Maritimes', 
                color_discrete_sequence= [cnf])
    fig.update_traces(textposition='outside')
    #fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    fig_html = mpld3.fig_to_html(plt.gcf())
    return HttpResponse(fig_html)