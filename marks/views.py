from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Student
from marks.models import StudentModuleMark

# Create your views here.
@login_required #being logged in required to view page, if not logged in then if statement below will not run
def StudentMarks_View(request): #function to return StudentMarks template on request
    if not hasattr(request.user, "student"): #since login is required, the user must be either a staff or student currently 
        return redirect("StaffDashboard") #so if a staff tried to load the students page to view marks using the url they will be redirected to the staff dashboard
    
    student = request.user.student #get logged in student object
    moduleMarks = StudentModuleMark.objects.filter(student = student) #get all of the students studentmoduleMark records

    markedTotal = 0 #total to calculate overall average of fully marked modules
    markedCount = 0 #count of how many modules have been fully marked
    classification = None #initilase classification with none to account for if no classification is calculated yet (this is not a final students classification, this is just to show what a student is currently averaging)
    overallAverage = None

    for moduleMark in moduleMarks:
        if moduleMark.mark1 is not None and moduleMark.mark2 is not None: #checks if both marks have been entered for a module
            moduleMark.avg = (moduleMark.mark1 + moduleMark.mark2)/2 #add a runtime attribute to moduleMark, doesnt actually exist or save to the database but can be used to temporarily add a feild to the object 
            markedTotal = markedTotal + moduleMark.avg #add the average for the module to the total 
            markedCount = markedCount + 1 #increment count of modules fully marked by 1
    
    if markedCount > 0: #if there is at least 1 fully marked module then calculate the overall average for the student
        overallAverage = markedTotal/markedCount #calculate overall average from marked modules
        if overallAverage >= 70:
            classification = "First Class"
        elif overallAverage >= 60:
            classification = "Upper Second Class"
        elif overallAverage >= 50:
            classification = "Lower Second Class"
        elif overallAverage >= 40:
            classification = "Third Class"
        else:
            classification = "Fail"


    return render(request, 'StudentMarks.html', {"student":student, "moduleMarks":moduleMarks, "classification":classification, "overallAverage":overallAverage}) #returns StudentMarks template and student record and students modulemark records and the classification and overallAverage

@login_required #using login required deals with users not logged in attemping to access the page, if statement below deals with the weakness that a logged in user staff/student can load still load another type of users page
def StaffAddMarks_View(request): #function to return StaffAddMarks template on request and returns students
    if not hasattr(request.user, "staff"): #works the same as redirect in StudentMarks_view by checking if user is staff
        return redirect("StudentDashboard") #redirects student to the student dashboard if they try load a staffs page with url
    students = Student.objects.all()# get all student objects from Student table
    return render(request, 'StaffAddMarks.html', {"students":students}) #return the staddaddmarks page and students

@login_required #using login required deals with users not logged in attemping to access the page, if statement below deals with the weakness that a logged in user staff/student can load still load another type of users page
def StaffAddStudentMarks_View(request, studentid): #function to return StaffAddMarks template on request
    if not hasattr(request.user, "staff"): #works the same as redirect in StudentMarks_view by checking if user is staff
        return redirect("StudentDashboard") #redirects student to the student dashboard if they try load a staffs page with url
    
    try: #try statement just incase in the url a staff tries to manually enter an incorrect id
       student = Student.objects.get(id=studentid)#retrieve the student object from database using id entered in url
    except:
       return redirect("StaffAddMarks") #send back to StaffAddMarks page if incorrect id entered
    
    if request.method == "POST": #checks to see if method is post (checks if  form was posted)
      if "moduleMarkID" in request.POST: #checks if moduleMarkID in the from
          moduleMarkID = request.POST.get("moduleMarkID") #get moduleMarkID from form
          mark1 = request.POST.get("mark1").strip() #gets mark1 (currently a string)
          mark2 = request.POST.get("mark2").strip()

          try: #check if the modulemark record exists
              moduleMark = StudentModuleMark.objects.get(id=moduleMarkID) #get StudentModuleMark record by the id entered
          except:
              messages.error(request, "Modulemark not found")
              return redirect("StaffAddStudentMarks", studentid=student.id)
          
          if moduleMark.student != student: #check to see if the modulemark sent in the form belongs to the student being edited, this prevents someone using postman to send a different students modulemark id to edit 
              messages.error(request, "Cannot update this students marks")
              return redirect("StaffAddStudentMarks", studentid=student.id)

          if mark1 == "" or mark1 == "None": #if the mark1 field is left empty then set it to none (not 0 since we dont want to mess up a student's mark average)
              moduleMark.mark1 = None #set value of mark1 to none (null/no value in datbase)
          else:
              try: #try to convert mark entered into float
                  mark1float = float(mark1) #convert string to float
              except: #catches exception to prevent crash
                  messages.error(request, "Please enter valid number") #error message if non number entered
                  return redirect("StaffAddStudentMarks", studentid=student.id) #redirects back to same page
              
              if mark1float < 0 or mark1float > 100:
                  messages.error(request, "Please enter a number between 0 and 100")
                  return redirect("StaffAddStudentMarks", studentid=student.id)
              moduleMark.mark1 = mark1float

          if mark2 == "" or mark2 == "None": #if the mark2 field is left empty then set it to none (not 0 since we dont want to mess up a student's mark average)
              moduleMark.mark2 = None #set value of mark2 to none
          else:
              try:
                  mark2float = float(mark2) #convert string to float
              except:
                  messages.error(request, "Please enter valid number")
                  return redirect("StaffAddStudentMarks", studentid=student.id)
              
              if mark2float < 0 or mark2float > 100:
                  messages.error(request, "Please enter a number between 0 and 100")
                  return redirect("StaffAddStudentMarks", studentid=student.id)
              moduleMark.mark2 = mark2float

          moduleMark.save() #saves changes to the specfimoduleMark 
          messages.success(request, "Marks updated successfully")
          return redirect("StaffAddStudentMarks", studentid=student.id)
    
    moduleMarks = StudentModuleMark.objects.filter(student=student)
    return render(request, 'StaffAddStudentMarks.html', {"student":student, "moduleMarks":moduleMarks})