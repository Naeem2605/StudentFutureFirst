from django.shortcuts import render, redirect
from accountDetails.models import Module
from accountDetails.models import Topic
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
@login_required #being logged in required to view page
def RecommendModule_View(request): #function for recommending a module to student
    if not hasattr(request.user, "student"): #since login is required, the user must be either a staff or student currently 
        return redirect("StaffDashboard") #so if a staff tried to load the student recommend module page using the url they will be redirected to the staff dashboard
    
    recommendedModules = None #initialises as none at first to prevent the template from attemting to to display the recommended modules before any topics entered yet
    if request.method == "POST":
        topicsIDs = request.POST.getlist("topicsIDs") #get list of topic ids entered

        if not topicsIDs: #checks if no topics entered
            messages.error(request, "Please select at least one topic")
            return redirect("RecommendModule")
        
        recommendedModules = Module.objects.filter(topics__id__in=topicsIDs).distinct()#filter to get all modules which are related to the topics entered, only distinct records shown to prevent duplicates
        
    topics = Topic.objects.all()
    return render(request, "RecommendModule.html", {"recommendedModules":recommendedModules, "topics":topics})

@login_required #being logged in required to view page
def ManageModules_View(request): #function to add or delete modules
    if not hasattr(request.user, "staff"): #works the same as redirect in RecommendModule_View by checking if user is staff
        return redirect("StudentDashboard") #redirects student to the student dashboard if they try load a staffs page with url
    
    if request.method == "POST":
        if "name" in request.POST: # if name is in the request then
            name = request.POST.get("name").strip() #get module name from filled out form and store in name
            code = request.POST.get("code").strip()# strip removes leading and trailing spaces
            description = request.POST.get("description").strip()
            topicsIDs = request.POST.getlist("topicsIDs") #get list of topic ids for the topics selected

            if not name or not code or not description or not topicsIDs: #checks if any fields are empty
                messages.error(request, "All fields must be entered") #if any empty than display error
                return redirect("ManageModules")#redirect back to ManageModules page to remove entered fields

            if Module.objects.filter(name=name).exists():#check entire Module table to see if module name already exists
                messages.error(request, "This module already exists")#if it exists create error message
                return redirect("ManageModules") #redirect back to ManageModules page to remove entered fields
            
            if Module.objects.filter(code=code).exists():#check entire Module table to see if module code already exists
                messages.error(request, "This module already exists")#if it exists create error message
                return redirect("ManageModules") #redirect back to ManageModules page to remove entered fields
            
            module = Module.objects.create( #create new Module with details entered in form and store object in variable 
            name = name,
            code = code,
            description = description
            )

            for topicID in topicsIDs: #iterates through all topicIDs entered
                module.topics.add(topicID) #adds eachs topicid entered into the join table between module and topic 
            messages.success(request, "Module Created successfully")
            return redirect("ManageModules")

        elif "moduleID" in request.POST: #if moduleid is in the request then
            moduleID = request.POST.get("moduleID").strip() #strip even though passed in hidden field, helps prevent errors caused by an edited form
            try: #check if module exists
                module = Module.objects.get(id=moduleID) #retrieve module by its id and store in module
            except:
                messages.success(request, "Module not found")
                return redirect("ManageModules")
            module.delete() #delete module
            messages.success(request, "Module Deleted successfully")
            return redirect("ManageModules")

    modules = Module.objects.all() #retrieve all modules in module table 
    topics = Topic.objects.all()
    return render(request, "ManageModules.html", {"modules": modules, "topics":topics})

@login_required #being logged in required to view page
def StaffManageMyModules_View(request): #function for staff to manage the modules they teach  
    if not hasattr(request.user, "staff"): #works the same as redirect in RecommendModule_View by checking if user is staff
        return redirect("StudentDashboard") #redirects student to the student dashboard if they try load a staffs page with url
    
    staff = request.user.staff #retrives logged in staff object

    if request.method == "POST":
        if "moduleID" in request.POST: # if moduleID is in the request then
            moduleID = request.POST.get("moduleID").strip()
            try: #check if module exists, this helps prevent crash if a module is deleted by another staff whilst the current staff is attempting to add or delete a module from their record
                module = Module.objects.get(id=moduleID) #retrieve the modules selected from the module table
            except:
                messages.error(request, "Module not found")
                return redirect("StaffManageMyModules")

            if staff.module.filter(id=moduleID).exists(): #check to see if this staff teaches this module already by checking the many to many table using the modules id
                staff.module.remove(module) #remove the module if they already teach it
                messages.success(request, "Module removed from your profile successfully")
            else:
                staff.module.add(module)#add module to staffs many to many table with module
                messages.success(request, "Module added to your profile successfully")
            return redirect("StaffManageMyModules") #redirect back to same page, this prevent form trying to resubmit
        
    modules = Module.objects.all() #retrieve all modules in module table
    staffsModules = staff.module.all() #retrives all of staffs current modules
    return render(request, "StaffManageMyModules.html", {"modules":modules, "staffsModules":staffsModules})
    
