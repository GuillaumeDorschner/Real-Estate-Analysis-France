from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('analyse/', views.analyse, name='analyse'),
    path('analyse/<str:annee>/', views.analyse_annee, name='analyse_page'),
]
