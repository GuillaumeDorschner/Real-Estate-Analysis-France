from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .analyse.test import analyse_data

def index(request):
    return render(request, "index.html")

def analyse(request):
    # Obtenir l'image analysée
    plot_data = analyse_data(request)

    # Ajouter l'image au contexte
    context = {
        "var": "heyyy",
        "plot": plot_data
    }
    
    # Charger le template et retourner la réponse
    template = loader.get_template("analyse/index.html")
    return HttpResponse(template.render(context, request))


def about(request):
    return render(request, "about.html")
