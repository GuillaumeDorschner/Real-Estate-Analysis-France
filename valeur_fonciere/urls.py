from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('analyse/', views.analyse, name='analyse'),
    path('analyse/inter/', views.analyse_inter, name='analyse_inter'),
    path('analyse/<str:annee>/', views.analyse_intra, name='analyse_intra'),
    path('get_graph/<str:type>/<str:annee>/<str:graph>/<str:filtre>', views.get_graph, name='get_graph')
]