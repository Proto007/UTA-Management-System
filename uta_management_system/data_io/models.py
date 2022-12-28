from django.db import models

class DataIO(models.Model):
    """
    A django model to represent a file containing UTA schedules.

    ...

    Attributes
    ----------
    file_link : FileField
        link to the file (google spreadsheet)

    """
    file_link = models.URLField(max_length=200, default="")
