from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.models import Student
from accountDetails.models import Module
from marks.models import StudentModuleMark
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages

# Create your views here.
@login_required #being logged in required to view page
def CreateOrDeleteStudent_View(request):
    if not hasattr(request.user, "staff"): #works the same as redirect in studentdetails_view
        return redirect("StudentDashboard") #redirects student to the student dashboard if they try load a staffs page with url
    
    if request.method == "POST": #if request method is post then
        if "username" in request.POST: # if username is in the request then
          username = request.POST.get("username", "").strip() #get username from filled out form and store in username
          firstName = request.POST.get("firstName").strip()# strip removes leading and trailing spaces
          lastName = request.POST.get("lastName").strip()
          email = request.POST.get("email").strip()
          password = request.POST.get("password").strip()
          studentID = request.POST.get("studentID").strip()
          modulesIDs = request.POST.getlist("modulesIDs") #get the ids for the list of modules entered


          if not username or not firstName or not lastName or not email or not password or not studentID or not modulesIDs: #checks if any fields are empty
            messages.error(request, "All fields must be entered") #if any empty than display error
            return redirect("CreateOrDeleteStudent")#redirect back to CreateOrDeleteStudent page to remove entered fields

          if User.objects.filter(username=username).exists():#check entire user to see if username already exists
            messages.error(request, "This username already exists")#if it exists create error message
            return redirect("CreateOrDeleteStudent") #redirect back to register page to remove entered fields
        
          if User.objects.filter(email=email).exists():#check entire user to see if email already exists
            messages.error(request, "This email already exists")#if it exists create error message
            return redirect("CreateOrDeleteStudent")
        
          if Student.objects.filter(studentID=studentID).exists():#check entire Student tabel to see if studentID already exists
            messages.error(request, "This staffID already exists")#if it exists create error message
            return redirect("CreateOrDeleteStudent")
        
          try: # this try statement is used to handle invalid password error
            validate_password(password) #try this line to verify if password is valid
          except ValidationError as e:
            for error in e.messages: #loops through all errors valid for the specfic situation
              messages.error(request, error) #if password not valid, display error messages
            return redirect("CreateOrDeleteStudent")#redirect back to CreateOrDeleteStudent page if not valid


          user = User.objects.create_user( #create new user with details entered in form and store in user variable
            username = username,
            first_name = firstName,
            last_name = lastName,
            email = email,
            password = password
          )

          student = Student.objects.create( #create Student entry linked to the just created user, store in student variable to be used later
            user = user,
            studentID = studentID #unique staffid
          )

          for moduleID in modulesIDs: #iterates through every module id in the variable modulesIDs
            StudentModuleMark.objects.create( #create new entry into StudentModuleMark for every module chosen by the user
                student = student, #links every module record to the student just created
                module_id = moduleID #module id for the module is stored as a foreign key
            )
        elif "studentID" in request.POST: #if studentID is in the request then
            studentID = request.POST.get("studentID") #no need to strip as studentID isnt user entered, its gained from hidden field passed from form
            student = Student.objects.get(id=studentID) #retrieve student by its id and store in student
            student.delete() #delete topic
        
    modules = Module.objects.all() #retrieve all modules in Module table
    students = Student.objects.all()
    return render(request, "CreateOrDeleteStudent.html", {"modules": modules, "students": students}) # redirect back to CreateOrDeleteStudent page and return data

@login_required #being logged in required to view page
def StudentDetails_View(request): #function to return StudentDetails template on request
    if not hasattr(request.user, "student"): #since login is required, the user must be either a staff or student currently 
        return redirect("StaffDashboard") #so if a staff tried to load the student details page using the url they will be redirected to the staff dashboard
    return render(request, 'StudentDetails.html')

@login_required
def StaffDetails_View(request): #function to return StaffDetails template on request
    if not hasattr(request.user, "staff"): #works the same as redirect in studentdetails_view
        return redirect("StudentDashboard") #redirects student to the student dashboard if they try load a staffs page with url
    return render(request, 'StaffDetails.html')