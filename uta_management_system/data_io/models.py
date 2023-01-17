"""
Defines multiple models that work together to create the checkin system
"""
from django.core.validators import MinLengthValidator
from django.db import models


class DataIO(models.Model):
    """
    `DataIO` model contains a `file_link` field from where the UTA schedule is obtained
    """

    file_link = models.URLField(max_length=200, default="")


class Shift(models.Model):
    """
    `Shift` model represents a single shift
    """

    # <Day: Description> used to limit choices for field `day`
    DAYS = (
        ("Monday", "Shift is on Mondays"),
        ("Tuesday", "Shift is on Tuesdays"),
        ("Wednesday", "Shift is on Wednesdays"),
        ("Thursday", "Shift is on Thursdays"),
        ("Friday", "Shift is on Fridays"),
    )
    description = models.CharField(
        max_length=30
    )  # sample `description`: "MON 12:00 - 13:30"
    day = models.CharField(
        max_length=10, choices=DAYS
    )  # `day` has to be within the weekdays
    start = models.TimeField(
        auto_now=False, auto_now_add=False
    )  # `start` is a `datetime.datetime.time` object
    end = models.TimeField(
        auto_now=False, auto_now_add=False
    )  # `end` is a `datetime.datetime.time` object


class UTA(models.Model):
    """
    `UTA` model represents a single UTA
    """

    fullname = models.CharField(
        max_length=100, default=""
    )  # UTA fullname (e.g. Hugh Mann)
    emplid = models.CharField(
        max_length=8, validators=[MinLengthValidator(8)]
    )  # UTA's 8 digit unique CUNY empl ID
    shifts = models.ManyToManyField(
        Shift
    )  # reference to multiple `Shift` objects that the UTA is assigned to work in


class RandomPass(models.Model):
    """
    `RandomPass` contains a `random_pass` field which is randomly generated each day
    """

    random_pass = models.CharField(max_length=100, default="")


class Checkin(models.Model):
    """
    `Checkin` model contains instances of successful checkins by the UTA to their assigned Shift(s)
    """

    created_at = models.DateTimeField(auto_now_add=True)  # checkin time
    # <Day: Description> provides choices for alternate schedule
    DAYS = (
        ("", "Not an alternate schedule"),
        ("Monday", "Monday schedule"),
        ("Tuesday", "Tuesday schedule"),
        ("Wednesday", "Wednesday schedule"),
        ("Thursday", "Thursday schedule"),
        ("Friday", "Friday schedule"),
    )
    emplid = models.CharField(
        max_length=8, validators=[MinLengthValidator(8)]
    )  # UTA's 8 digit unique CUNY empl ID
    shift = models.ForeignKey(
        Shift, on_delete=models.CASCADE
    )  # allows many `Checkin` objects to reference single `Shift` object
    late_mins = models.IntegerField(
        default=0
    )  # stores how late the checkin is from the `shift` start time
    number_of_shifts = models.IntegerField(
        default=1
    )  # allows checkin for consecutive shifts
    covered_by = models.CharField(
        max_length=8, blank=True, null=True, validators=[MinLengthValidator(8)]
    )  # nullable field storing the empl ID of UTA who is covering (if they are covering)
    alternate_day = models.CharField(
        max_length=10, choices=DAYS, default=""
    )  # allows checkin to another day of the week if CUNY is following alternate day schedule


class TimeSheet(models.Model):
    """
    `TimeSheet` model allows creation timesheets given two dates
    """

    start_date = models.DateField()
    end_date = models.DateField()
