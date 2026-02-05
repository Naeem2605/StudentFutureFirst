from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.models import Student
from marks.models import StudentModuleMark



# Create your views here.
@login_required #login required to view page
def StudentDashboard_View(request): #function to return studentdashboard template on request
    if not hasattr(request.user, "student"): #since login is required, the user must be either a staff or student currently 
        return redirect("StaffDashboard") #so if a staff tried to load the student dashboard using the url they will be redirected to the staff dashboard
    
    student = request.user.student
    moduleMarks = StudentModuleMark.objects.filter(student = student)
    return render(request, 'StudentDashboard.html', {"student": student, "moduleMarks": moduleMarks}) #returns Studentdashboard template

@login_required
def StaffDashboard_View(request):
    if not hasattr(request.user, "staff"): #works the same as redirect in StudentDashboard_view
        return redirect("StudentDashboard") #redirects student to the student dashboard if they try load a staffs page with url
    return render(request, 'StaffDashboard.html') #returns Staffdashboard template