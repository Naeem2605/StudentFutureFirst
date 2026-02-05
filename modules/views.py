from django.shortcuts import render, redirect
from accountDetails.models import Module
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
@login_required #being logged in required to view page
def RecommendModule_View(request):
    if not hasattr(request.user, "student"): #since login is required, the user must be either a staff or student currently 
        return redirect("StaffDashboard") #so if a staff tried to load the student recommend module page using the url they will be redirected to the staff dashboard
    return render(request, "RecommendModule.html")

@login_required #being logged in required to view page
def ManageModules_View(request): #function to add or delete modules
    if not hasattr(request.user, "staff"): #works the same as redirect in RecommendModule_View by checking if user is staff
        return redirect("StudentDashboard") #redirects student to the student dashboard if they try load a staffs page with url
    
    if request.method == "POST":
        if "name" in request.POST: # if name is in the request then
            name = request.POST.get("name").strip() #get module name from filled out form and store in name
            code = request.POST.get("code").strip()# strip removes leading and trailing spaces
            description = request.POST.get("description").strip()

            if not name or not code or not description: #checks if any fields are empty
                messages.error(request, "All fields must be entered") #if any empty than display error
                return redirect("ManageModules")#redirect back to ManageModules page to remove entered fields

            if Module.objects.filter(name=name).exists():#check entire Module table to see if module name already exists
                messages.error(request, "This module already exists")#if it exists create error message
                return redirect("ManageModules") #redirect back to ManageModules page to remove entered fields
            
            if Module.objects.filter(code=code).exists():#check entire Module table to see if module code already exists
                messages.error(request, "This module already exists")#if it exists create error message
                return redirect("ManageModules") #redirect back to ManageModules page to remove entered fields
            
            Module.objects.create( #create new Module with details entered in form 
            name = name,
            code = code,
            description = description
            )

        elif "moduleID" in request.POST: #if moduleid is in the request then
            moduleID = request.POST.get("moduleID") #no need to strip as moduleid isnt user entered, its gained from hidden field passed from form
            module = Module.objects.get(id=moduleID) #retrieve module by its id and store in module
            module.delete() #delete module

    modules = Module.objects.all #retrieve all modules in model table 
    return render(request, "ManageModules.html", {"modules": modules})
    
