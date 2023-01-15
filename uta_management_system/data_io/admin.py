from django.contrib import admin

from .models import *

# register the models to the Django admin debug site
admin.site.register(DataIO)
admin.site.register(Shift)
admin.site.register(UTA)
admin.site.register(RandomPass)
admin.site.register(Checkin)
