from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.models import Student
from accountDetails.models import Module, Availability
from marks.models import StudentModuleMark
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

# Create your views here.
@login_required #being logged in required to view page
def ManageStudents_View(request):
    if not hasattr(request.user, "staff"): #works the same as redirect in studentdetails_view
        return redirect("StudentDashboard") #redirects student to the student dashboard if they try load a staffs page with url
    
    if request.method == "POST": #if request method is post then (checks to see if a form was posted first)
        if "username" in request.POST: # if username is in the request then
          username = request.POST.get("username").strip() #get username from filled out form and store in username
          firstName = request.POST.get("firstName").strip()# strip removes leading and trailing spaces
          lastName = request.POST.get("lastName").strip()
          email = request.POST.get("email").strip()
          password = request.POST.get("password").strip()
          confirmPassword = request.POST.get("confirmPassword").strip()
          studentID = request.POST.get("studentID").strip()
          modulesIDs = request.POST.getlist("modulesIDs") #get the ids for the list of modules entered


          if not username or not firstName or not lastName or not email or not password or not confirmPassword or not studentID or not modulesIDs: #checks if any fields are empty
            messages.error(request, "All fields must be entered") #if any empty than display error
            return redirect("ManageStudents")#redirect back to ManageStudents page to remove entered fields
          
          if password != confirmPassword: #check if passwords match
            messages.error(request, "Passwords do not match")
            return redirect("ManageStudents")#redirect back to ManageStudents page to remove entered fields
          
          if User.objects.filter(username=username).exists():#check entire user to see if username already exists
            messages.error(request, "This username already exists")#if it exists create error message
            return redirect("ManageStudents") #redirect back to register page to remove entered fields
        
          if User.objects.filter(email=email).exists():#check entire user to see if email already exists
            messages.error(request, "This email already exists")#if it exists create error message
            return redirect("ManageStudents")
        
          if Student.objects.filter(studentID=studentID).exists():#check entire Student tabel to see if studentID already exists
            messages.error(request, "This studentID already exists")#if it exists create error message
            return redirect("ManageStudents")
        
          try: # this try statement is used to handle invalid password error
            validate_password(password) #try this line to verify if password is valid
          except ValidationError as e:
            for error in e.messages: #loops through all errors valid for the specfic situation
              messages.error(request, error) #if password not valid, display error messages
            return redirect("ManageStudents")#redirect back to ManageStudents page if not valid


          user = User.objects.create_user( #create new user with details entered in form and store new instance in user variable
            username = username,
            first_name = firstName,
            last_name = lastName,
            email = email,
            password = password
          )

          student = Student.objects.create( #create Student entry linked to the just created user, store in student variable to be used later
            user_id = user.id, #store just created user id as foreign key to link user to student
            studentID = studentID #unique studentid (not the id of the student record itself)
          )

          for moduleID in modulesIDs: #iterates through every module id in the variable modulesIDs
            StudentModuleMark.objects.create( #create new entry into StudentModuleMark for every module chosen by the user
                student_id = student.id, #links every module record to the student just created
                module_id = moduleID #module id for the module is stored as a foreign key
            )
          messages.success(request, "Student Created successfully")
          return redirect("ManageStudents")
        elif "studentid" in request.POST: #if studentID is in the request then we know its to activate/deactivate student account
            studentid = request.POST.get("studentid").strip()
            try: #check to see if student exists, prevents crash if a modified form is submitted via something like postman and student id enetred doesnt exist
               student = Student.objects.get(id=studentid) #retrieve student by its id and store in student
            except:
               messages.error(request, "Student not found")
               return redirect("ManageStudents")
            student.user.is_active = not student.user.is_active #when button is clicked, the status of is_active is inverted to go from true to false and vice versa
            if student.user.is_active == True: #check if after the change, is students account active and display message accordingly
               messages.success(request, "Student's account activated successfully")
            else:
               messages.success(request, "Student's account deactivated successfully")
            student.user.save() #saves changes to the user record in db
            return redirect("ManageStudents")
        
    modules = Module.objects.all() #retrieve all modules in Module table
    students = Student.objects.all()
    return render(request, "ManageStudents.html", {"modules": modules, "students": students}) # redirect back to ManageStudents page and return data

@login_required #being logged in required to view page
def StudentDetails_View(request): #student edits their profile page
    if not hasattr(request.user, "student"): #since login is required, the user must be either a staff or student currently 
        return redirect("StaffDashboard") #so if a staff tried to load the student details page using the url they will be redirected to the staff dashboard
    
    student = request.user.student #stores logged in student object

    if request.method == "POST": #if request method is post then (checks to see if a form was posted first)
        if "firstName" in request.POST: # if firstname is in the request then
          username = request.POST.get("username").strip()
          firstName = request.POST.get("firstName").strip()# strip removes leading and trailing spaces
          lastName = request.POST.get("lastName").strip()

          if not firstName or not lastName or not username: #checks if any fields are empty
            messages.error(request, "All fields must be entered") #if any empty than display error
            return redirect("StudentDetails")#redirect back to StudentDetails page to remove entered fields
          
          if User.objects.filter(username=username).exclude(id=student.user.id).exists(): #checks entire user table to see if username already exists, excluding the current logged in users username
            messages.error(request, "This username is taken") #if username taken display error
            return redirect("StudentDetails")
                 
          student.user.username = username
          student.user.first_name = firstName #store updated data
          student.user.last_name = lastName
          student.user.save()  #saves changes to student's user record
          messages.success(request, "Details updated successfully")
          return redirect("StudentDetails")
        elif "currentPassword" in request.POST:
           currentPassword = request.POST.get("currentPassword").strip() #get current password enetered
           newPassword = request.POST.get("newPassword").strip()
           confirmNewPassword = request.POST.get("confirmNewPassword").strip()

           if not currentPassword or not newPassword or not confirmNewPassword: #checks if any fields are empty
              messages.error(request, "All fields must be entered") #if any empty than display error
              return redirect("StudentDetails")#redirect back to StudentDetails page to remove entered fields
       
           if not student.user.check_password(currentPassword): #check if pass enetered is equal to users current password
              messages.error(request, "Current password is incorrect")
              return redirect("StudentDetails")
       
           if not newPassword == confirmNewPassword: #check if new pass and confirm new pass do not match
              messages.error(request, "New password and confirm password do not match")
              return redirect("StudentDetails")

           try: # this try statement is used to handle invalid password error
                validate_password(newPassword) #try this line to verify if new password is valid
           except ValidationError as e:
                for error in e.messages: #loops through all errors valid for the specfic situation
                  messages.error(request, error) #if password not valid, display error messages
                return redirect("StudentDetails")#redirect back to StudentDetails page if not valid   
       
           student.user.set_password(newPassword) #hashes the new password and updates the old one
           student.user.save() #saves changes
           update_session_auth_hash(request, student.user) #updates session with new user object as password just changed so old session holding onto previous user object is invalid
           messages.success(request, "Password updated successfully")
           return redirect("StudentDetails")

    return render(request, 'StudentDetails.html', {"student": student}) #return studentdetails page and logged in student object

@login_required
def StaffDetails_View(request): #staff edit their profile page
    if not hasattr(request.user, "staff"): #works the same as redirect in studentdetails_view
        return redirect("StudentDashboard") #redirects student to the student dashboard if they try load a staffs page with url
    
    staff = request.user.staff #stores logged in staff object

    if request.method == "POST": #if request method is post then (checks to see if a form was posted first)
        if "firstName" in request.POST: # checks if firstname in form to know what form to deal with
          firstName = request.POST.get("firstName").strip()# strip removes leading and trailing spaces
          lastName = request.POST.get("lastName").strip()
          officeRoom = request.POST.get("officeRoom").strip()
          username = request.POST.get("username").strip()

          if not firstName or not lastName or not officeRoom or not username: #checks if any fields are empty
            messages.error(request, "All fields must be entered") #if any empty than display error
            return redirect("StaffDetails")#redirect back to StaffDetails page to remove entered fields
          
          if User.objects.filter(username=username).exclude(id=staff.user.id).exists(): #checks entire user table to see if username already exists, excluding the current logged in users username
            messages.error(request, "This username is taken") #if username taken display error
            return redirect("StaffDetails")
          
          staff.officeRoom = officeRoom
          staff.user.username = username
          staff.user.first_name = firstName #store updated data
          staff.user.last_name = lastName
          staff.save() #save changes to staff record
          staff.user.save()  #saves changes to staff's user record
          messages.success(request, "Details updated successfully")
          return redirect("StaffDetails")
        elif "currentPassword" in request.POST:
           currentPassword = request.POST.get("currentPassword").strip() #get current password enetered
           newPassword = request.POST.get("newPassword").strip()
           confirmNewPassword = request.POST.get("confirmNewPassword").strip()

           if not currentPassword or not newPassword or not confirmNewPassword: #checks if any fields are empty
              messages.error(request, "All fields must be entered") #if any empty than display error
              return redirect("StaffDetails")#redirect back to StaffDetails page to remove entered fields
           
           if not newPassword == confirmNewPassword: #check if new pass and confirm new pass do not match
              messages.error(request, "New password and confirm password do not match")
              return redirect("StaffDetails")
       
           if not staff.user.check_password(currentPassword): #check if pass enetered is equal to users current password
              messages.error(request, "Current password is incorrect")
              return redirect("StaffDetails")
      
           try: # this try statement is used to handle invalid password error
                validate_password(newPassword) #try this line to verify if new password is valid
           except ValidationError as e:
                for error in e.messages: #loops through all errors valid for the specfic situation
                  messages.error(request, error) #if password not valid, display error messages
                return redirect("StaffDetails")#redirect back to StaffDetails page if not valid   
       
           staff.user.set_password(newPassword) #hashes the new password and updates the old one
           staff.user.save() #saves changes
           update_session_auth_hash(request, staff.user) #updates session with new user object as password just changed so old session holding onto previous user object is invalid
           messages.success(request, "Password updated successfully")
           return redirect("StaffDetails")
    return render(request, 'StaffDetails.html', {"staff": staff})

@login_required
def EditStudent_View(request, studentid): #function for staff editing student details using student id passed from url
    if not hasattr(request.user, "staff"): #works the same as redirect in studentdetails_view
        return redirect("StudentDashboard") #redirects student to the student dashboard if student trys load a staffs page with url
    
    try: #try statement just incase in the url a staff tries to manually enter an incorrect id
       student = Student.objects.get(id=studentid)#retrieve the student object from database using id entered in url
    except:
       messages.error(request, "Student does not exist")
       return redirect("ManageStudents") #send back to manage students page
    
    if request.method == "POST": #checks to see if method is post (checks if  form was posted)
       if "firstName" in request.POST: #checks if firstname in the from
           firstName = request.POST.get("firstName").strip()# strip removes leading and trailing spaces
           lastName = request.POST.get("lastName").strip()
           email = request.POST.get("email").strip()
      
           if not firstName or not lastName or not email: #checks if any fields are empty
               messages.error(request, "All fields must be entered") #if any empty than display error
               return redirect("EditStudent", studentid=student.id)#redirect back to EditStudent page to remove entered fields, send the students id along when calling the editstudent view again
      
           if User.objects.filter(email=email).exclude(id=student.user.id).exists(): #checks entire user table to see if email already exists, excluding the current logged in users email
               messages.error(request, "This email is taken") #if email taken display error
               return redirect("EditStudent", studentid=student.id)
      
           student.user.first_name = firstName #update details with new details
           student.user.last_name = lastName
           student.user.email = email
           student.user.save() #saves the updated details in the student's user record

           messages.success(request, "Student details updated successfully") #display success message if updated
           return redirect("EditStudent", studentid=student.id)
       elif "moduleID" in request.POST: # if moduleID is in the request then either add or delete a module for the student
            moduleID = request.POST.get("moduleID").strip() #even though this is takem from hidden field, still strip as someone using postman may send a different input
            try: #check to see if module exists, can help with concurrent users
               module = Module.objects.get(id=moduleID) #retrieve the modules selected from the module table
            except:
               messages.error(request, "Module not found")
               return redirect("EditStudent", studentid=student.id) #send back to same page while passing the students id again to ensure staff can see the same student details again when page reloads

            existingModuleMark = StudentModuleMark.objects.filter(student=student, module=module) #get all existing studentmodulemark records where the moduleid for the module entered matches an existing one for that specfic student
            if existingModuleMark.exists(): #check to see if this student already takes this module
                existingModuleMark.delete() #remove the module if they already have it on request
                messages.success(request, "Module removed from student record successfully")
            else:
                StudentModuleMark.objects.create( #create new entry into StudentModuleMark if it doesnt already exist for that student
                student_id = student.id, #links studentmodulemark record to the student using studentid as foreign key
                module_id = moduleID #module id for the module is stored as a foreign key
            )
                messages.success(request, "Module added to student record successfully")
            return redirect("EditStudent", studentid=student.id) #redirect back to same page, this prevent form trying to resubmit
    moduleMarks = StudentModuleMark.objects.filter(student = student) #get all of a students modulemark records
    studentsModules = [] #initialise a list (list needed to store students modules, since you cant compare a studentmodulemark record to a module record directly)
    for moduleMark in moduleMarks: #iterate through all modulemark records
       studentsModules.append(moduleMark.module) #add the modulemark's module to the list to be able to check in the template if the student is already taking the module

    modules = Module.objects.all() #retrieve all modules in module table
    return render(request, 'EditStudent.html', {"student":student, "studentsModules":studentsModules,"modules":modules}) #render editstudent page and pass student object to the page so it can be prefilled with the students data, and also students module info

@login_required
def StaffManageMyAvailability_View(request): #function for staff to manage their availability slots
   if not hasattr(request.user, "staff"): #works the same as redirect in RecommendModule_View by checking if user is staff
        return redirect("StudentDashboard") #redirects student to the student dashboard if they try load a staffs page with url
    
   staff = request.user.staff #retrives logged in staff object

   if request.method == "POST": #check if form submitted
      if "day" in request.POST: #check if day in the form submitted
         day = request.POST.get("day").strip() #get day from filled out form
         startTime = request.POST.get("startTime").strip()
         endTime = request.POST.get("endTime").strip()

         if not day or not startTime or not endTime: #check if any field left empty
             messages.error(request, "All fields must be entered") #if any empty than display error
             return redirect("StaffManageMyAvailability")
         
         if startTime >= endTime: #check to see if start time entered is incorrectly greater than the endtime
            messages.error(request, "Start time must be before the end time")
            return redirect("StaffManageMyAvailability")
         
         availability = Availability.objects.create( #create new availabilty with details entered
            day = day,
            startTime = startTime,
            endTime = endTime
         )

         staff.availability.add(availability) #add just created availabilty slot to join table between staff and availabilty
         messages.success(request, "Availabilty slot added successfully")
         return redirect("StaffManageMyAvailability")
      elif "availabilityID" in request.POST: #if the availabilityid is in the request then we know the deletion form was submitted to delete an availability 
         availabilityID = request.POST.get("availabilityID")
         try: #check to see if the availabilty exists  
            availability = Availability.objects.get(id=availabilityID) #retrive the availabilty slot clicked for deletion
         except:
            messages.error(request, "Availability not found")
            return redirect("StaffManageMyAvailability")

         if availability not in staff.availability.all(): #check to see if the availabilty record belongs to this staff, this prevents the deletion of another staffs availabilty through the use of changing what id is sent in the form (mabye using postman)
            messages.error(request, "Cannot delete this availability slot")
            return redirect("StaffManageMyAvailability")
         
         availability.delete() #delete the availability
         messages.success(request, "Availability slot deleted successfully")
         return redirect("StaffManageMyAvailability")
    
   staffAvailability = staff.availability.all()# get all of a staffs availabilty slots to display to them
   return render(request, "StaffManageMyAvailability.html", {"staffAvailability":staffAvailability})