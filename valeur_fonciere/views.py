from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .analyse.graph import *
import os
import pandas as pd

def index(request):
    return render(request, "index.html")

def analyse(request):


    directory = './data/annee_traitee'
    pages = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            pages.append(filename.split('.')[0])
            print(filename)

    print(pages)

    context = {
        "pages": pages,
    }
    
    # Charger le template et retourner la réponse
    template = loader.get_template("analyse/index.html")
    return HttpResponse(template.render(context, request))


def about(request):
    return render(request, "about.html")

def analyse_intra(request, annee):
    if os.path.isfile('./data/annee_traitee/'+annee+'.csv'):
        df = pd.read_csv('./data/annee_traitee/'+annee+'.csv',sep=';',header=0)
        context = {
            "graph": graph_region('regions',df),
            "Vente_mois" : Vente_par_Mois(df),
            "topPlusMoinsCher" : topPlusMoinsCher(df),
        }
    else :
        context = {"var":"Pas de données pour cette année"}

    template = loader.get_template("analyse/template_intra.html")
    return HttpResponse(template.render(context, request))


def analyse_inter(request, annee):
    if os.path.isfile('./data/annee_traitee/'+annee+'.csv'):
        df = pd.read_csv('./data/annee_traitee/'+annee+'.csv',sep=';',header=0)
        context = {
            "graph": graph_region('regions',df),
            "Vente_mois" : Vente_par_Mois(df),
            "topPlusMoinsCher" : topPlusMoinsCher(df),
        }
    else :
        context = {"var":"Pas de données pour cette année"}

    template = loader.get_template("analyse/template_inter.html")
    return HttpResponse(template.render(context, request))

