from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from io import StringIO
import matplotlib.pyplot as plt
import numpy as np

import matplotlib
matplotlib.use('agg')

def index(request):
    return render(request, "index.html")


def analyse(request):
    # Création des données
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    # Tracer la courbe
    plt.plot(x, y)

    # Ajouter des labels et un titre
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Un exemple de courbe sinusoïdale')

    # Stocker le graphique sous forme d'image
    imgdata = StringIO()
    plt.savefig(imgdata, format='svg')
    imgdata.seek(0)

    # Ajouter l'image au contexte
    context = {
        "var": "heyyy",
        "plot": imgdata.getvalue()
    }
    
    # Charger le template et retourner la réponse
    template = loader.get_template("analyse/index.html")
    return HttpResponse(template.render(context, request))


def about(request):
    return render(request, "about.html")
