from io import StringIO
import matplotlib.pyplot as plt
import numpy as np

import matplotlib
matplotlib.use('agg')

def analyse_data(request):
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

    # Renvoyer l'image
    return imgdata.getvalue()
