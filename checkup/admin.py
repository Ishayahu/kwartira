from django.contrib import admin
from checkup.models import *
# Register your models here.

admin.site.register(Visit)
admin.site.register(OnePeopleRoom)
admin.site.register(TwoPeopleRoom)
admin.site.register(ThreePeopleRoom)
admin.site.register(UserProfile)