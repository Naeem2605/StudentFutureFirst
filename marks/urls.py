from django.urls import path
from . import views

urlpatterns = [
    path('StudentMarks/', views.StudentMarks_View, name ='StudentMarks'), #calls StudentMarks_View to display StudentMarks.html template at StudentMarks/ path
    path('StaffAddMarks/', views.StaffAddMarks_View, name ='StaffAddMarks'),
]