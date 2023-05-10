from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from io import StringIO
import matplotlib.pyplot as plt
import numpy as np


def index(request):
    return render(request, "index.html")


def analyse(request):

    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    plt.plot(x, y)

    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Un exemple de courbe sinusoïdale')

    imgdata = StringIO()
    plt.savefig(imgdata, format='svg')
    imgdata.seek(0)

    context = {"var": "heyyy", "plot": imgdata.getvalue()}

    template = loader.get_template("analyse/index.html")
    return HttpResponse(template.render(context, request))


def about(request):
    return render(request, "about.html")
