import os
import sys
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from .analyse.graph import *
import pandas as pd



print("Loading data...\n")

# -------------test data----------------
directory = './data/annee_traitee'
pages = []

for filename in os.listdir(directory):
    if os.path.isfile(os.path.join(directory, filename)):
        pages.append(filename.split('.')[0])

df ={} 

pages.sort(reverse=True)

df['2022'] = pd.read_csv('./data/annee_traitee/2022.csv',sep=';',header=0, low_memory=False)



# # -------------all data----------------
# # import the csv data
# directory = './data/annee_traitee'
# pages = []

# total_files = len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])

# for filename in os.listdir(directory):
#     if os.path.isfile(os.path.join(directory, filename)):
#         pages.append(filename.split('.')[0])

# pages.sort(reverse=True)

# df = {}

# for index, annee in enumerate(pages):
#     sys.stdout.write("\rFile : {} / {}".format(index+1, total_files))
#     sys.stdout.flush()
#     df[annee] = pd.read_csv('./data/annee_traitee/'+annee+'.csv',sep=';',header=0,  low_memory=False)

# print("\nData loaded ✅\n")



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

    context = {
        "annee": annee
    }

    template = loader.get_template("analyse/template_intra.html")
    return HttpResponse(template.render(context, request))


def analyse_inter(request):

    template = loader.get_template("analyse/template_inter.html")
    return HttpResponse(template.render(context, request))

def get_graph(request, type, annee,graph, filtre):


    if type == "inter":
        print("inter")

    else:
        dfTemp = df[annee]

        if graph == "repartionTypeBien":
            return repartionTypeBien(request, dfTemp, filtre)
        elif graph == "heatMap":
            return heatmap(request, dfTemp, filtre)
        else:
            raise Http404("Graph does not exist")