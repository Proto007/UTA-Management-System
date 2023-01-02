from django.db import models
from django.core.validators import MinLengthValidator

class DataIO(models.Model):
    file_link = models.URLField(max_length=200, default="")

class Shift(models.Model):
    DAYS = (
        ('Monday', 'Shift is on Mondays'),
        ('Tuesday', 'Shift is on Tuesdays'),
        ('Wednesday', 'Shift is on Wednesdays'),
        ('Thursday', 'Shift is on Thursdays'),
        ('Friday', 'Shift is on Fridays')
    )
    # Sample description: "MON 12:00 - 13:30"
    description = models.CharField(max_length=30)
    day = models.CharField(max_length=10, choices=DAYS)
    start = models.TimeField(auto_now=False, auto_now_add=False)
    end = models.TimeField(auto_now=False, auto_now_add=False)

class UTA(models.Model):
    lastname = models.CharField(max_length=100, default="")
    firstname = models.CharField(max_length=100, default="")
    emplid = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    shifts = models.ManyToManyField(Shift)

class RandomPass(models.Model): 
    random_pass = models.CharField(max_length=100, default="")

class Checkin(models.Model):
    emplid = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    shift = models.ManyToManyField(Shift)
    late_mins = models.IntegerField(default=0)
    number_of_shifts = models.IntegerField(default=1)
