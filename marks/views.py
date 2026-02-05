from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required #being logged in required to view page, if not logged in then if statement below will not run
def StudentMarks_View(request): #function to return StudentMarks template on request
    if not hasattr(request.user, "student"): #since login is required, the user must be either a staff or student currently 
        return redirect("StaffDashboard") #so if a staff tried to load the students page to view marks using the url they will be redirected to the staff dashboard
    return render(request, 'StudentMarks.html') #returns StudentMarks template

@login_required #using login required deals with users not logged in attemping to access the page, if statement below deals with the weakness that a logged in user staff/student can load still load another type of users page
def StaffAddMarks_View(request): #function to return StaffAddMarks template on request
    if not hasattr(request.user, "staff"): #works the same as redirect in StudentMarks_view by checking if user is staff
        return redirect("StudentDashboard") #redirects student to the student dashboard if they try load a staffs page with url
    return render(request, 'StaffAddMarks.html')