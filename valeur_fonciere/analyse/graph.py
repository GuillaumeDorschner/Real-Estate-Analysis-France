import folium
import json
import matplotlib.pyplot as plt
import base64
import mpld3
import matplotlib.colors as mcolors
import plotly
import pandas as pd
import numpy as np
import plotly.subplots as sp
import plotly.graph_objects as go
import matplotlib
from branca.colormap import linear
from django.http import HttpResponse
matplotlib.use('Agg')
import plotly.express as px
from pretty_html_table import build_table


def repartition_type_bien(request,df):
    plt.cla()
    type_counts = df['Type local'].value_counts()
    fig, ax = plt.subplots(figsize=(10,10))
    type_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
    plt.grid(False)
    ax.set_ylabel('')
    plt.axis('off')
    ax.set_title('Répartition des types de biens')
    html_fig = mpld3.fig_to_html(fig)
    fig.clear()
    plt.close()
    return HttpResponse(html_fig)

def top_5(request,data):
    """top 5 des départements les plus chers"""
    departement = json.load(open("./data/departements/departements_dict.json"))
    m2 = data[(data["Type local"] != "Dépendance")& (data["Type local"] != "Local industriel. commercial ou assimilé")].reset_index(drop = True)
    print(m2['Code departement'].nunique())
    m2["carrez_sum"] = m2["Surface Carrez du 1er lot"].fillna(0)  +  m2["Surface Carrez du 2eme lot"].fillna(0) + m2["Surface Carrez du 3eme lot"].fillna(0) + m2["Surface Carrez du 4eme lot"].fillna(0) + m2["Surface Carrez du 5eme lot"].fillna(0)
    m2["Prix mètre carré"] = np.where(m2["carrez_sum"] != 0,m2["Valeur fonciere"]/m2["carrez_sum"],m2["Valeur fonciere"]/m2["Surface reelle bati"])
    m2 = m2.drop(np.where(m2['Prix mètre carré'] > 25000)[0])
    prix_m2_departement = m2.groupby('Code departement',as_index=False)['Prix mètre carré'].mean()
    top5_chers = pd.DataFrame(prix_m2_departement.sort_values(by="Prix mètre carré",ascending=False).head(5))
    for i in top5_chers["Code departement"]:
        top5_chers.loc[top5_chers["Code departement"] == i,"Département"] = departement.get(str(i))
    top5_moins_chers = pd.DataFrame(prix_m2_departement.sort_values(by="Prix mètre carré",ascending=True).head(5))

    for i in top5_moins_chers["Code departement"]:
        top5_moins_chers.loc[top5_moins_chers["Code departement"] == i,"Département"] = departement.get(str(i))
    
    top5_chers = top5_chers.drop(columns="Code departement")
    top5_moins_chers = top5_moins_chers.drop(columns="Code departement")
    cher = build_table(top5_chers, 'red_light')
    moinscher = build_table(top5_moins_chers, 'green_light')
    html_table = f'<div class="flex"><div>{cher}</div><div>{moinscher}</div></div>'
    return HttpResponse(html_table)


def vol_monetaire(request,df):
    """Volume monétaire par département
    graph fixe"""
    DEPARTMENTS = json.load(open("./data/departements/departements_dict.json")) 
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
    image_html = plotly.io.to_html(fig)
    return HttpResponse(image_html)

def prix_m2(request,df):
    """Calcul du prix moyen au m2 par département
    graph non interactif"""
    df['Valeur fonciere par m2'] = df['Valeur fonciere'] / df['Surface terrain']
    prix_m2_departement = df.groupby('Code departement')['Valeur fonciere par m2'].mean()
    return prix_m2_departement

def heat_map(request,df):

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

def nb_ventes(request,df):
    """Nombre de ventes par département
    graph fixe"""
    dict_nb_ventes = pd.DataFrame(df["Code departement"].value_counts()).reset_index()
    dict_nb_ventes.columns = ["Code departement", "Nombre de ventes"]
    departements = json.load(open("./data/departements/departements_dict.json"))
    for i in dict_nb_ventes["Code departement"]:
        dict_nb_ventes.loc[dict_nb_ventes["Code departement"] == i, "Département"] = departements[i]

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

    #fig.update_xaxes(range=[50000, 110000], row=1, col=1)

    #fig.update_xaxes(range=[1000, 4000], row=1, col=2)
    
    fig_html = plotly.io.to_html(fig)
    return HttpResponse(fig_html)

def evo_m2(request,data):
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

    fig = px.line(temp, x="Month mutation", y="Value", color='Departements', log_y=True, color_discrete_sequence=[dth, rec,act])
    retour = plotly.io.to_html(fig)
    plt.close()
    return HttpResponse(retour)

def nb_ventes_par_mois(request,data):
    """Nombre de ventes par mois
    graph fixe"""
    df = pd.DataFrame(data)
    df["Date mutation"] =pd.to_datetime(df['Date mutation'],dayfirst=True).dt.strftime('%y-%m')
    plt.figure(figsize=(8,3))
    plt.title('Nombre de ventes répartis par mois')
    plt.plot(df["Date mutation"].value_counts()[df['Date mutation'].unique()])
    plt.xticks(rotation=45)
    plt.xlabel('Date')
    plt.ylabel('Nombre de ventes')
    html_fig = mpld3.fig_to_html(plt.gcf())
    plt.close()
    return HttpResponse(html_fig)

def evo_m_Carrez (request,df):
    dth = '#ff2e63' 
    rec = '#21bf73'
    act = '#fe9801'
    temp = df[(df["Type local"] != "Dépendance")& (df["Type local"] != "Local industriel. commercial ou assimilé")].reset_index(drop = True)
    temp["Month mutation"] = pd.to_datetime(temp["Date mutation"]).dt.month
    temp["carrez_sum"] = temp["Surface Carrez du 1er lot"].fillna(0)  +  temp["Surface Carrez du 2eme lot"].fillna(0) + temp["Surface Carrez du 3eme lot"].fillna(0) + temp["Surface Carrez du 4eme lot"].fillna(0) + temp["Surface Carrez du 5eme lot"].fillna(0)
    temp["Prix mètre carré"] = np.where(temp["carrez_sum"] != 0,temp["Valeur fonciere"]/temp["carrez_sum"],temp["Valeur fonciere"]/temp["Surface reelle bati"])
    temp = temp.drop(np.where(temp['Prix mètre carré'] > 25000)[0])

    temp['Prix mètre carré 2018'] = temp[pd.to_datetime(temp["Date mutation"]).dt.year == 2018]["Valeur fonciere"]/temp[pd.to_datetime(temp["Date mutation"]).dt.year == 2018]["Surface reelle bati"]
    temp['Prix mètre carré 2019'] = temp[pd.to_datetime(temp["Date mutation"]).dt.year == 2019]["Valeur fonciere"]/temp[pd.to_datetime(temp["Date mutation"]).dt.year == 2019]["Surface reelle bati"]
    temp['Prix mètre carré 2022'] = temp[pd.to_datetime(temp["Date mutation"]).dt.year == 2022]["Valeur fonciere"]/temp[pd.to_datetime(temp["Date mutation"]).dt.year == 2022]["Surface reelle bati"]

    temp =temp.replace(np.inf, np.nan)

    # temp['No. of Recovered to 1 Death Case'] = round(temp['Recovered']/temp['Deaths'], 3)
    temp = temp.groupby('Month mutation')["Prix mètre carré 2018","Prix mètre carré 2019","Prix mètre carré 2022"].mean().reset_index()

    temp = temp.melt(id_vars='Month mutation', value_vars=['Prix mètre carré 2018','Prix mètre carré 2019','Prix mètre carré 2022'], 
                    var_name='Departements', value_name='Value')

    fig = px.line(temp, x="Month mutation", y="Value", color='Departements', log_y=True, color_discrete_sequence=[dth, rec,act])
    fig_html = plotly.io.to_html(fig)
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
        

def graph_dynamique_valfonciere(request,data):
    dth = '#ff2e63' 
    rec = '#21bf73'
    cnf  = '#fe9801'
    temp = data.copy()
    temp = temp[(temp["Type local"] != "Dépendance") & (temp["Type local"] != "Local industriel. commercial ou assimilé")].reset_index(drop = True)
    temp['Prix mètre carré'] = temp['Valeur fonciere']/temp['Surface reelle bati']
    temp['Region'] = temp.apply(location, axis=1)
    temp = temp.groupby('Region')['Prix mètre carré'].mean().reset_index()
    temp = temp.melt(id_vars='Region', value_vars=['Prix mètre carré'], 
                    var_name='Case', value_name='Count').sort_values('Count')
    temp.head()
    fig = px.bar(temp, y='Region', x='Count', color='Case', barmode='group', orientation='h',
                text='Count', 
                color_discrete_sequence= [dth, rec, cnf])
    fig.update_traces(textposition='outside')
    #fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    fig_html = plotly.io.to_html(fig)
    return HttpResponse(fig_html)

def graph_dynamique_m2(request,data):
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
                text='Count', animation_frame='Date',
                color_discrete_sequence= [dth, rec, cnf])
    fig.update_traces(textposition='outside')
    #fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    fig_html = plotly.io.to_html(fig)
    return HttpResponse(fig_html)

def Heat_Map2(request,data):
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

    return HttpResponse(m._repr_html_())

def Surface_Carrez(request,data):
    m2 = data[(data["Type local"] != "Dépendance")& (data["Type local"] != "Local industriel. commercial ou assimilé")].reset_index(drop = True)
    m2["carrez_sum"] = m2["Surface Carrez du 1er lot"].fillna(0)  +  m2["Surface Carrez du 2eme lot"].fillna(0) + m2["Surface Carrez du 3eme lot"].fillna(0) + m2["Surface Carrez du 4eme lot"].fillna(0) + m2["Surface Carrez du 5eme lot"].fillna(0)
    m2["Prix mètre carré"] = np.where(m2["carrez_sum"] != 0,m2["Valeur fonciere"]/m2["carrez_sum"],m2["Valeur fonciere"]/m2["Surface reelle bati"])
    m2 = m2.drop(np.where(m2['Prix mètre carré'] > 25000)[0])
    property_changes = m2.groupby('Code departement',as_index=False)['Prix mètre carré'].mean()

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
    return HttpResponse(m._repr_html_())

def Nb_piece(request,data):
    act = '#fe9801'
    temp = data[(data["Type local"] != "Dépendance")& (data["Type local"] != "Local industriel. commercial ou assimilé")].reset_index(drop = True)
    temp = temp.groupby(['Code departement'])['Nombre pieces principales'].mean().reset_index()
    temp.columns = ["Code departement","Nombre pieces principales"]
    temp["Nombre pieces principales"] = round(temp["Nombre pieces principales"],1)
    departements = json.load(open("./data/departements/departements_dict.json"))
    for i in temp["Code departement"]:
        temp.loc[temp["Code departement"] == i,"Département"] = departements.get(str(i))
        
    temp

    temp = temp.sort_values('Code departement', ascending=False)

    fig = px.bar(temp.sort_values('Nombre pieces principales', ascending=False).head(10).sort_values('Nombre pieces principales', ascending=True), 
                x="Nombre pieces principales", y="Code departement", text='Nombre pieces principales', orientation='h', 
                width=700, height=600, range_x = [0, 7])
    fig.update_traces(marker_color=act, opacity=0.8, textposition='outside')
    fig_html = plotly.io.to_html(fig)
    return HttpResponse(fig_html)