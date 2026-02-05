from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from accounts.models import Staff
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def Homepage(request):
    return render(request, 'Homepage.html') #returns homepage template

@login_required
def RecommendLecturer_View(request):
    if not hasattr(request.user, "student"): #since login is required, the user must be either a staff or student currently 
        return redirect("StaffDashboard") #so if a staff tried to load the student recommend lecturer page using the url they will be redirected to the staff dashboard
    return render(request, "RecommendLecturer.html")

def Logout_View(request):
    logout(request) #logouts logged in user
    return redirect("Homepage") #redirects back to homepage after logout

def Login_View(request): #function to login
    if request.method == "POST":#if request method is post then
        username = request.POST.get("username") #get username from filled out form and store in username
        password = request.POST.get("password") 

        user = authenticate(request, username = username, password = password) #authenticate user and if authenticated then store user in user

        if user is None: #if user doesnt exist with those details then
            messages.error(request, "Invalid username or password") #create error message to then be displayed
            return redirect("Login") #redirect back to login page to remove entered fields
        else:
            login(request, user) #keeps user details to stay logged in
            if hasattr(user, "staff"): #if user is a staff then redirect to staffdashboard
                return redirect("StaffDashboard")
            else: #forms to create users require a staff id or student id so no records can exist without them, no need to check if student
                return redirect("StudentDashboard")
            
    return render(request, 'Login.html') #load login page

def Register_View(request): #register staff function
    if request.method == "POST": #if request method is post then
        username = request.POST.get("username", "").strip() #get username from filled out form and store in username
        firstName = request.POST.get("firstName").strip()# strip removes leading and trailing spaces
        lastName = request.POST.get("lastName").strip()
        email = request.POST.get("email").strip()
        password = request.POST.get("password").strip()
        staffID = request.POST.get("staffID").strip()

        if not username or not firstName or not lastName or not email or not password or not staffID: #checks if any fields are empty
            messages.error(request, "All fields must be entered") #if any empty than display error
            return redirect("Register")#redirect back to register page to remove entered fields

        if User.objects.filter(username=username).exists():#check entire user to see if username already exists
            messages.error(request, "This username already exists")#if it exists create error message
            return redirect("Register") #redirect back to register page to remove entered fields
        
        if User.objects.filter(email=email).exists():#check entire user to see if email already exists
            messages.error(request, "This email already exists")#if it exists create error message
            return redirect("Register")
        
        if Staff.objects.filter(staffID=staffID).exists():#check entire Staff tabel to see if staffid already exists
            messages.error(request, "This staffID already exists")#if it exists create error message
            return redirect("Register")
        
        try: # this try statement is used to handle invalid password error
            validate_password(password) #try this line to verify if password is valid
        except ValidationError as e:
            for error in e.messages: #loops through all errors valid for the specfic situation
              messages.error(request, error) #if password not valid, display error messages
            return redirect("Register")#redirect back to register page if not valid


        user = User.objects.create_user( #create new user with details entered in form 
            username = username,
            first_name = firstName,
            last_name = lastName,
            email = email,
            password = password
        )

        Staff.objects.create( #create staff entry linked to the just created user
            user = user,
            staffID = staffID #unique staffid
        )

        return redirect("Login") # redirect back to login page

    return render(request, 'Register.html') #load register page