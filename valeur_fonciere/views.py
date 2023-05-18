import os
import sys
import pandas as pd
from django.http import Http404
from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .analyse.graph import *


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
    return HttpResponse(template.render())

@csrf_exempt
def get_graph(request, type, annee, graph):
    filters = {}
    if request.method == 'POST':
        filters = json.loads(request.body)

    if type == "inter":
        print("inter")
        dfTemp = filter_df(dfTemp, filters)

    else:
        dfTemp = df[annee]
        dfTemp = filter_df(dfTemp, filters)

        if graph == "Vente_par_Mois":
            return Vente_par_Mois(request, dfTemp)
        elif graph == "repartionTypeBien":
            return repartionTypeBien(request, dfTemp)
        elif graph == "data_departement":
            return data_departement(request, dfTemp)
        elif graph == "top5cher":
            return top5cher(request, dfTemp)
        elif graph == "top5moinscher":
            return heatMap(request, dfTemp)
        elif graph == "prix_m2":
            return prix_m2(request, dfTemp)
        elif graph == "heatMap":
            return heatMap(request, dfTemp)
        else:
            raise Http404("Graph does not exist")

def filter_df(df, filters):
    for key, value in filters.items():
        if key in df.columns:
            df = df[df[key] == value]
        else:
            return Http404("Filter does not exist")
    return df