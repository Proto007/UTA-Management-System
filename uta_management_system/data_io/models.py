from django.db import models

class DataIO(models.Model):
    """
    A django model to represent a file containing UTA schedules.
    
    ...

    Attributes
    ----------
    file : FileField
        file uploaded by the user
    file_type : str
        type of the file("txt","csv" etc.)

    """
    file = models.FileField(max_length=10000, upload_to="schedules")
    file_type = models.CharField(max_length=10)
