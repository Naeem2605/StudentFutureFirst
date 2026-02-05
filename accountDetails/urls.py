from django.urls import path
from . import views

urlpatterns = [
    path('StudentDetails/', views.StudentDetails_View, name ='StudentDetails'), #calls views.StudentDetails_View to display StudentDetails.html template at StudentDetails/ path
    path('StaffDetails/', views.StaffDetails_View, name ='StaffDetails'),
    path('CreateOrDeleteStudent/', views.CreateOrDeleteStudent_View, name ='CreateOrDeleteStudent'),
]