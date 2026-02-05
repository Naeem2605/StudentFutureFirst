from django.urls import path
from . import views

urlpatterns = [
    path('ManageModules/', views.ManageModules_View, name ='ManageModules'), #calls ManageModules_View to display ManageModules.html template at ManageModules/ path
    path('RecommendModule/', views.RecommendModule_View, name ='RecommendModule')
]