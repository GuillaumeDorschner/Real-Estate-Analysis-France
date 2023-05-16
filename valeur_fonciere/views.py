from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .analyse.graph import *
import time
import os
import pandas as pd
from django.http import JsonResponse



print("Loading data...")

directory = './data/annee_traitee'
pages = []

for filename in os.listdir(directory):
    if os.path.isfile(os.path.join(directory, filename)):
        pages.append(filename.split('.')[0])

df ={} 

df['2022'] = pd.read_csv('./data/annee_traitee/2022.csv',sep=';',header=0, low_memory=False)

# # import the csv data
# directory = './data/annee_traitee'
# pages = []

# for filename in os.listdir(directory):
#     if os.path.isfile(os.path.join(directory, filename)):
#         pages.append(filename.split('.')[0])

# print(pages)

# df = []

# for annee in pages:
#     df[annee] = pd.read_csv('./data/annee_traitee/'+annee+'.csv',sep=';',header=0)


print("Data loaded")

def index(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")

def analyse(request):
    context = {
        "pages": pages,
    }
    
    template = loader.get_template("analyse/index.html")
    return HttpResponse(template.render(context, request))

def analyse_intra(request, annee):
    # if os.path.isfile('./data/annee_traitee/'+annee+'.csv'):
    #     df = pd.read_csv('./data/annee_traitee/'+annee+'.csv',sep=';',header=0)
    #     context = {
    #         "graph": graph_region('regions',df),
    #         "Vente_mois" : Vente_par_Mois(df),
    #         "topPlusMoinsCher" : topPlusMoinsCher(df),
    #     }
    # else :
    #     context = {"var":"Pas de données pour cette année"}
    # template = loader.get_template("analyse/template_intra.html")
    # return HttpResponse(template.render(context, request))

    context = {
        "annee": annee
    }

    template = loader.get_template("analyse/template_intra.html")
    return HttpResponse(template.render(context, request))


def analyse_inter(request):
#     if os.path.isfile('./data/annee_traitee/'+annee+'.csv'):
#         df = pd.read_csv('./data/annee_traitee/'+annee+'.csv',sep=';',header=0)
#         context = {
#             "graph": graph_region('regions',df),
#             "Vente_mois" : Vente_par_Mois(df),
#             "topPlusMoinsCher" : topPlusMoinsCher(df),
#         }
#     else :
#         context = {"var":"Pas de données pour cette année"}

#     template = loader.get_template("analyse/template_inter.html")
#     return HttpResponse(template.render(context, request))
    return None

def get_graph(request, annee, graph, filtre):

    dfTemp = df[annee]

    if graph == "repartionTypeBien":
        return repartionTypeBien(request, dfTemp, filtre)
    else:
        return JsonResponse({"graph": "https://t4.ftcdn.net/jpg/00/97/58/97/360_F_97589769_t45CqXyzjz0KXwoBZT9PRaWGHRk5hQqQ.jpg"})