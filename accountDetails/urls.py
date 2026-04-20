from django.urls import path
from . import views

urlpatterns = [
    path('StudentDetails/', views.StudentDetails_View, name ='StudentDetails'), #calls views.StudentDetails_View to display StudentDetails.html template at StudentDetails/ path
    path('StaffDetails/', views.StaffDetails_View, name ='StaffDetails'),
    path('ManageStudents/', views.ManageStudents_View, name ='ManageStudents'),
    path('EditStudent/<int:studentid>', views.EditStudent_View, name ='EditStudent'), #gets student id thats passed in the url and sends it to editstudent_view as parameter
    path('StaffManageMyAvailability', views.StaffManageMyAvailability_View, name ='StaffManageMyAvailability'),
]