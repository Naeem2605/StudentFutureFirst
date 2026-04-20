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
            
            Topic.objects.create(name=name)#create new Topic with details entered in form 
            messages.success(request, "Topic Created successfully")
            return redirect("ManageTopics")

        elif "topicID" in request.POST: #if topicID is in the request then we know the delete topic form was submitted
            topicID = request.POST.get("topicID").strip()
            try: #check to see if topic exists, can help if someone using postman attempts to enter an incorrect id into the hidden field, or if another staff already deleted the topic on their side
                topic = Topic.objects.get(id=topicID) #retrieve topic by its id and store in topic
            except:
                messages.error(request, "Topic not found")
                return redirect("ManageTopics")
            topic.delete() #delete topic
            messages.success(request, "Topic deleted successfully")
            return redirect("ManageTopics")

    topics = Topic.objects.all() #retrieve all topics in Topic table
    return render(request, "ManageTopics.html", {"topics": topics})

@login_required #being logged in required to view page
def StaffManageMyTopics_View(request): #function for staff to manage the topics they specialse in  
    if not hasattr(request.user, "staff"): #works the same as redirect in RecommendModule_View by checking if user is staff
        return redirect("StudentDashboard") #redirects student to the student dashboard if they try load a staffs page with url
    
    staff = request.user.staff #retrives logged in staff object

    if request.method == "POST":
        if "topicID" in request.POST: # if topicID is in the request then
            topicID = request.POST.get("topicID").strip()
            try: #check if topic exists
                topic = Topic.objects.get(id=topicID) #retrieve the topic selected from the topic table
            except:
                messages.error(request, "Topic not found")
                return redirect("StaffManageMyTopics")

            if staff.topics.filter(id=topicID).exists(): #check to see if this staff specialises in this topic already by checking the many to many table using the topicid
                staff.topics.remove(topic) #remove the topic if they already specialise in it
                messages.success(request, "Topic removed from your profile successfully")
            else:
                staff.topics.add(topic)#add topic to staffs many to many table with topic
                messages.success(request, "Topic added to your profile successfully")
            return redirect("StaffManageMyTopics") #redirect back to same page, this prevents form trying to resubmit
        
    topics = Topic.objects.all() #retrieve all topics in topic table
    staffsTopics = staff.topics.all() #retrives all of staffs current topics
    return render(request, "StaffManageMyTopics.html", {"topics":topics, "staffsTopics":staffsTopics})



