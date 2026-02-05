from django.urls import path
from . import views

urlpatterns = [
    path('StudentDashboard/', views.StudentDashboard_View, name ='StudentDashboard'), #calls StudentDashboard_View to display studentdashboard.html template at studentdashboard/ path
    path('StaffDashboard/', views.StaffDashboard_View, name ='StaffDashboard'),
]