from django.shortcuts import render, redirect
from accountDetails.models import Topic
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
@login_required #being logged in required to view page
def ManageTopics_View(request):
    if not hasattr(request.user, "staff"): #since login is required, the user must be either a staff or student currently 
        return redirect("StudentDashboard") #so if a student tried to load the ManageTopics page using the url they will be redirected to the student dashboard
    
    if request.method == "POST":
        if "name" in request.POST: # if name is in the request then
            name = request.POST.get("name").strip() #get topic name from filled out form and store in name

            if not name: #checks if any fields are empty
                messages.error(request, "All fields must be entered") #if any empty than display error
                return redirect("ManageTopics")#redirect back to ManageTopics page to remove entered fields

            if Topic.objects.filter(name=name).exists():#check entire Topic table to see if Topic name already exists
                messages.error(request, "This topic already exists")#if it exists create error message
                return redirect("ManageTopics") #redirect back to ManageTopics page to remove entered fields
            
            Topic.objects.create( #create new Topic with details entered in form 
            name = name
            )

        elif "topicID" in request.POST: #if topicID is in the request then
            topicID = request.POST.get("topicID") #no need to strip as topicID isnt user entered, its gained from hidden field passed from form
            topic = Topic.objects.get(id=topicID) #retrieve topic by its id and store in topic
            topic.delete() #delete topic

    topics = Topic.objects.all #retrieve all topics in Topic table
    return render(request, "ManageTopics.html", {"topics": topics})



