from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from accounts.models import Staff
from accountDetails.models import Availability, Topic
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit

# Create your views here.
def Homepage(request):
    return render(request, 'Homepage.html') #returns homepage template

def Logout_View(request):
    logout(request) #logouts logged in user
    return redirect("Homepage") #redirects back to homepage after logout

@ratelimit(key='post:username', rate='10/m', method=['POST'], block=True) #limit a username to 10 requests a minute to prevent brute force of a single account, even if an ip block is bypassed
@ratelimit(key='ip', rate='10/m', method=['POST'], block=True) #limit an ip to 10 login requests a minute to help prevent brute force attacks
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
            else: #forms to create users require a staff id or student id so no records can exist without them, no need to check if student. If system is scaled later then a further if statement condition can be implemented 
                return redirect("StudentDashboard")
            
    return render(request, 'Login.html') #load login page

@ratelimit(key='post:email', rate='15/h', method=['POST'], block=True) #limit a single staffs email to 15 requests an hour
@ratelimit(key='ip', rate='15/h', method=['POST'], block=True) #limit an ip to 15 register requests a hour to help prevent abuse via the use of bots creating many accounts
def Register_View(request): #register staff function
    if request.method == "POST": #if request method is post then
        username = request.POST.get("username").strip() #get username from filled out form and store in username
        firstName = request.POST.get("firstName").strip()# strip removes leading and trailing spaces
        lastName = request.POST.get("lastName").strip()
        email = request.POST.get("email").strip()
        password = request.POST.get("password").strip()
        confirmPassword = request.POST.get("confirmPassword").strip()
        staffID = request.POST.get("staffID").strip()

        if not username or not firstName or not lastName or not email or not password or not confirmPassword or not staffID: #checks if any fields are empty
            messages.error(request, "All fields must be entered") #if any empty than display error
            return redirect("Register")#redirect back to register page to remove entered fields
        
        if password != confirmPassword: #check if passwords match
            messages.error(request, "Passwords do not match")
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

        Staff.objects.create( #create staff entry linked to the just created user. Using django ORM so no need for sql
            user_id = user.id,
            staffID = staffID #unique staffid
        )
        messages.success(request, "Registration successful, please Login")
        return redirect("Login") # redirect back to login page

    return render(request, 'Register.html') #load register page

@login_required
def RecommendLecturer_View(request):
    if not hasattr(request.user, "student"): #since login is required, the user must be either a staff or student currently 
        return redirect("StaffDashboard") #so if a staff tried to load the student recommend lecturer page using the url they will be redirected to the staff dashboard
    
    student = request.user.student #store logged in student object
    recommendedLecturers = None #initialises as none at first to prevent the template from attemting to to display the recommended lecturers before any topics entered yet
    if request.method == "POST":
        if "topicsIDs" in request.POST: #check if topicsid in the form and if so we know the student it searching for a recommended lecturer
            topicsIDs = request.POST.getlist("topicsIDs") #get list of topic ids entered

            if not topicsIDs: #checks if no topics entered
               messages.error(request, "Please select at least one topic")
               return redirect("RecommendLecturer")
        
            recommendedLecturers = Staff.objects.filter(topics__id__in=topicsIDs).distinct()#filter to get all staff which are related to the topics entered, only distinct records shown to prevent duplicates
        elif "availabilityID" in request.POST: #if availability id in the form then we know student is attempting to book a slot
            availabilityID = request.POST.get("availabilityID")

            try: #check to see if availabilty exists, helps with concurrent users if a staff deletes the availabilty before a student is able to book it
                availability = Availability.objects.get(id=availabilityID)
            except:# if it doesnt exist then message is shown
                messages.error(request, "Availability slot does not exist")
                return redirect("RecommendLecturer")
            
            if availability.student is None: # check if slot already booked, helps with concurrent users if a student books a availabilty and another student tries to book the same one without their page being up to date
                availability.student = student #link the logged in student to the availability slot
                availability.save() # save the changes to the availability record
                messages.success(request, "Availability slot booked successfully")
                return redirect("RecommendLecturer")
            else:
                messages.error(request, "Availability slot already taken") #if slot already has a student assigned to it then show error message
                return redirect("RecommendLecturer")
        else:#if no topics entered then form wasnt sent
            messages.error(request, "Please select at least one topic")
            return redirect("RecommendLecturer")
        
    topics = Topic.objects.all() #get all topics in Topic table to give student options
    return render(request, "RecommendLecturer.html", {"recommendedLecturers":recommendedLecturers, "topics":topics})