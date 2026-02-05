from django.urls import path
from . import views

urlpatterns = [
    path('ManageTopics/', views.ManageTopics_View, name ='ManageTopics'), #calls ManageTopics_View to display ManageTopics.html template at ManageTopics/ path
]