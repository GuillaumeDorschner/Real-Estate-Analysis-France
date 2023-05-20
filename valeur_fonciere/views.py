import os
import sys
import json
import pandas as pd
from django.http import Http404
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .analyse.graph import *
from json.decoder import JSONDecodeError




print("Loading data...\n")

# # -------------test data----------------
# directory = './data/annee_traitee'
# pages = []

# for filename in os.listdir(directory):
#     if os.path.isfile(os.path.join(directory, filename)):
#         pages.append(filename.split('.')[0])

# df ={} 

# pages.sort(reverse=True)

# df['2022'] = pd.read_csv('./data/annee_traitee/2022.csv',sep=',',header=0, low_memory=False)


with open('./data/regions/regions_dict.json', 'r') as f:
    data = json.load(f)

regions = list(data.keys())
departements = [dept for sublist in data.values() for dept in sublist]
departements.sort()

# -------------all data----------------
# import the csv data
directory = './data/annee_traitee'
pages = []

total_files = len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])

for filename in os.listdir(directory):
    if os.path.isfile(os.path.join(directory, filename)):
        pages.append(filename.split('.')[0])

pages.sort(reverse=True)

df = {}

for index, annee in enumerate(pages):
    sys.stdout.write("\rFile : {} / {}".format(index+1, total_files))
    sys.stdout.flush()
    df[annee] = pd.read_csv('./data/annee_traitee/'+annee+'.csv',sep=',',header=0,  low_memory=False)

print("\nData loaded ✅\n")



def index(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")

def analyse(request):
    context = {
        "pages": pages,
        'regions': regions,
        'departements': departements
    }
    
    template = loader.get_template("analyse/index.html")
    return HttpResponse(template.render(context, request))

def analyse_intra(request, annee:int):

    context = {
        "annee": annee,
        'regions': regions,
        'departements': departements
    }

    template = loader.get_template("analyse/template_intra.html")
    return HttpResponse(template.render(context, request))


def analyse_inter(request):

    template = loader.get_template("analyse/template_inter.html")
    return HttpResponse(template.render())

@csrf_exempt
def get_graph(request, type, annee, graph):
    filters = {}
    try:
        if request.method == 'POST':
            filters = json.loads(request.body)
    except JSONDecodeError:
        pass

    if type == "inter":
        dfTemp = {}

        df_all_years = pd.concat(df.values(), ignore_index=True)

        dfTemp = filter_df(df_all_years, filters)

        if graph =="top_5":
            return top_5(request, dfTemp)
        if graph =="repartition_type_bien":
            return repartition_type_bien(request, dfTemp)
        elif graph =="vol_monetaire":
            return vol_monetaire(request, dfTemp)
        elif graph == "heat_map":
            return heat_map(request, dfTemp)
        elif graph == "nb_ventes":
            return nb_ventes(request, dfTemp)
        elif graph == "evo_m2":
            return evo_m2(request, dfTemp)
        elif graph =="nb_ventes_par_mois":
            return nb_ventes_par_mois(request, dfTemp)
        elif graph == "evo_m_Carrez":
            return evo_m_Carrez(request, dfTemp)
        elif graph== "graph_dynamique_valfonciere":
            return graph_dynamique_valfonciere(request, dfTemp)
        elif graph=="graph_dynamique_m2":
            return graph_dynamique_m2(request, dfTemp)

    else:
        dfTemp = df[annee]
        dfTemp = filter_df(dfTemp, filters)
        if graph =="top_5":
            return top_5(request,dfTemp)
        if graph =="repartition_type_bien":
            return repartition_type_bien(request, dfTemp)
        elif graph =="vol_monetaire":
            return vol_monetaire(request, dfTemp)
        elif graph == "heat_map":
            return heat_map(request, dfTemp)
        elif graph == "nb_ventes":
            return nb_ventes(request, dfTemp)
        elif graph =="nb_ventes_par_mois":
            return nb_ventes_par_mois(request, dfTemp)
        elif graph== "graph_dynamique_valfonciere":
            return graph_dynamique_valfonciere(request, dfTemp)
        elif graph=="graph_dynamique_m2":
            return graph_dynamique_m2(request, dfTemp)
        elif graph == "Nb_piece":
            return Nb_piece(request, dfTemp)
        elif graph == "heat_map3":
            return heat_map3(request, dfTemp)
        else:
            raise Http404("Graph does not exist")


def filter_df(df, filters):
    for key, value in filters.items():
        if not value:
            continue

        if key == "start-date":
            df = df[df['Date mutation'] >= value]
        elif key == "end-date":
            df = df[df['Date mutation'] <= value]
        elif key == "price":
            df = df[df['Valeur fonciere'] == float(value)]
        elif key == "type":
            df = df[df['Type local'] == value]
        elif key == "surface-carrez-maximum":
            df = df[df['Surface Carrez du 1er lot'] <= float(value)]
        elif key == "departements":
            if filters.get("region-department-toggle", "off") == "on":
                df = df[df['Code departement'].isin(value)]
            else:
                df = df[~df['Code departement'].isin(value)]
        elif key == "regions":
            if filters.get("region-department-toggle", "off") == "on":
                df = df[df['Region'].isin(value)]
            else:
                df = df[~df['Region'].isin(value)]
        elif key == "region-department-toggle":
            continue
        else:
            raise Http404("Filter does not exist")

    return df
