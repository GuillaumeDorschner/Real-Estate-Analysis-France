from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .analyse.test import analyse_data
import os
import pandas as pd

def index(request):
    return render(request, "index.html")

def analyse(request):


    directory = './data/'
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
    if os.path.isfile('./data/valeursfoncieres-'+annee+'.txt'):
        f = open('./data/valeursfoncieres-'+annee+'.txt', 'r')
        data = f.read()
    context = {
        "var":data
    }

    template = loader.get_template("analyse/index.html")
    return HttpResponse(template.render(context, request))