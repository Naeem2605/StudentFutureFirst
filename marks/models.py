from django.db import models
from accounts.models import Student #imports student model from accounts app's models.py
from accountDetails.models import Module

# Create your models here.
class StudentModuleMark(models.Model): #manytomany join table created, extra attributes for marks
    student = models.ForeignKey(Student, on_delete=models.CASCADE) #foreign key linking StudentModuleMark join table to student table
    module = models.ForeignKey(Module, on_delete=models.CASCADE) #on deletion of module, studentmodulemarks entries are deleted
    mark1 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) #max 5 digits can be entered, can be null or blank
    mark2 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) #upto 2 decimal places