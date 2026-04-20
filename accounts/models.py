from django.db import models
from django.contrib.auth.models import User
from accountDetails.models import Topic, Availability, Module

# Create your models here.
class Student(models.Model): #create model for staff role
    user = models.OneToOneField(User, on_delete=models.CASCADE) #extends Djangos default User so we can add unique attributes, cascade deletes student entries if User is deleted
    studentID = models.CharField(max_length=20, unique=True) #students unique student id


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staffID = models.CharField(max_length=20, unique=True)
    officeRoom = models.CharField(max_length=20, blank=True, null=True) #allows staff to register without a office number needed
    topics = models.ManyToManyField(Topic, blank=True) #maps manytomany relation between staff and topic table and creates join table
    availability = models.ManyToManyField(Availability, blank=True)
    module = models.ManyToManyField(Module, blank=True)