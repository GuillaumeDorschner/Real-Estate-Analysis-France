from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .analyse.graph import *
import time
import os
import pandas as pd
from django.http import JsonResponse

def index(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")

def analyse(request):


    directory = './data/annee_traitee'
    pages = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            pages.append(filename.split('.')[0])

    context = {
        "pages": pages,
    }
    
    # Charger le template et retourner la réponse
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

    print(annee)
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
    if os.path.isfile('./data/annee_traitee/'+annee+'.csv'):
        df = pd.read_csv('./data/annee_traitee/'+annee+'.csv',sep=';',header=0)
        if graph == 'graph_region' and filtre == 'regions':
            graph_url = graph_region(filtre,df)
            return JsonResponse({'graph_url': graph_url})
    return JsonResponse({'graph_url': 'none'})
