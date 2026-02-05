from django.urls import path
from . import views

urlpatterns = [
    path('', views.Homepage, name='Homepage'), #homepage set with default url to display homepage first 
    path('Login/', views.Login_View, name ='Login'), #calls views.Login_View to display login.html template at login/ path
    path('Register/', views.Register_View, name ='Register'),
    path('Logout/', views.Logout_View, name ='Logout'),
    path('RecommendLecturer/', views.RecommendLecturer_View, name ='RecommendLecturer')
]