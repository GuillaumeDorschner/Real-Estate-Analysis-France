from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .analyse.test import analyse_data
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
        "var": "heyyy",
        "pages": pages
    }
    
    # Charger le template et retourner la réponse
    template = loader.get_template("analyse/index.html")
    return HttpResponse(template.render(context, request))


def about(request):
    return render(request, "about.html")

def analyse_annee(request, annee):
    print('./data/annee_traitee/'+annee+'.txt')
    if os.path.isfile('./data/annee_traitee/'+annee+'.txt'):
        f = open('./data/annee_traitee/'+annee+'.txt', 'r')
        data = f.read()
        print(data)
        context = {
        "var": data
    }
    else :
        context = {"var":"Pas de données pour cette année"}

    template = loader.get_template("analyse/template_annee.html")
    return HttpResponse(template.render(context, request))