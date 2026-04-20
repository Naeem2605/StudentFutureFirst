from django.db import models

# Create your models here.
class Topic(models.Model): #model to create Topic table in db
    name = models.CharField(max_length=100, unique=True) #topics name must be unique and have max length of 100 chars


class Availability(models.Model):
    day = models.CharField(max_length=15)
    startTime = models.TimeField() #allows attribute to store times
    endTime = models.TimeField()
    student = models.ForeignKey("accounts.Student", on_delete=models.SET_NULL, blank=True, null=True) #link student to specific availabilty booking, can be blank so no student needs to be assigned to the availabilty slot at creation, can be null to show a availabilty that isnt booked yet


class Module(models.Model):
    name = models.CharField(max_length=150, unique=True) #moduules name should be unique
    code = models.CharField(max_length=25) #module code number (not the same as modules ID)
    description = models.CharField(max_length=200)
    topics = models.ManyToManyField(Topic, blank=True)#many to many relation between module and topic tables, creates join table