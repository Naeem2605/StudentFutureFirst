from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.models import Student
from marks.models import StudentModuleMark
from django.contrib import messages
from accountDetails.models import Availability


# Create your views here.
@login_required #login required to view page
def StudentDashboard_View(request): #function to return studentdashboard template on request
    if not hasattr(request.user, "student"): #since login is required, the user must be either a staff or student currently 
        return redirect("StaffDashboard") #so if a staff tried to load the student dashboard using the url they will be redirected to the staff dashboard
    
    student = request.user.student #stores logged in student object

    if request.method == "POST":#checks if form sent to cancel a slot booking
        availabilityID = request.POST.get("availabilityID") #get id of availabilty that student wants to cancel

        try: #check to see if availabilty exists, helps with concurrent users if a staff deletes the availabilty before a student is able to delete it
            availability = Availability.objects.get(id=availabilityID)
        except:# if it doesnt exist then message is shown
            messages.error(request, "Availability slot does not exist")
            return redirect("StudentDashboard")
        
        if availability.student != student: #check to see if the availabilty belongs to the student (this is just incase for example postman is used to send a form which overwrites the hidden field, this would mean a student can delete another students booking)
            messages.error(request, "Cannot delete this availability slot")
            return redirect("StudentDashboard")
        
        availability.student = None #set the student field to none for that availabilty so it can be booked by another student
        availability.save() #save changes to the availabilty record
        messages.success(request, "Availabilty slot cancelled successfully")
        return redirect("StudentDashboard")
            
    availabilitySlotsBooked = Availability.objects.filter(student=student) #get all of a students booked slots
    for availabilitySlots in availabilitySlotsBooked: #iterate through all the availabilty records in the query set we recived in the line above
        for staff in availabilitySlots.staff_set.all(): #using the reverse relationship between the availabilty record and the staff who made it, iterate through all the staff who the availabilty is related to and store the staff in staff 
            availabilitySlots.staff = staff #set the just retrived staff to the availabilty record using a temporary runtime attribute (does not store in database nor have any relation to the feilds in the database)
          
    moduleMarks = StudentModuleMark.objects.filter(student = student) #uses logged in student id to filter for studentmodulemark records and stores them (.filter used is similar to where clause in sql and is able to retirve mutltiple rows)
    return render(request, 'StudentDashboard.html', {"student": student, "moduleMarks": moduleMarks, "availabilitySlotsBooked":availabilitySlotsBooked}) #returns Studentdashboard template

@login_required
def StaffDashboard_View(request):
    if not hasattr(request.user, "staff"): #works the same as redirect in StudentDashboard_view
        return redirect("StudentDashboard") #redirects student to the student dashboard if they try load a staffs page with url
    
    staff = request.user.staff #stores logged in student object
    staffModules = request.user.staff.module.all() #store logged in staffs modules they teach
    return render(request, 'StaffDashboard.html', {"staff": staff, "staffModules":staffModules}) #returns Staffdashboard template and logged in staffs details so staff name can be displayed, and also returns staffs modules they teach to display