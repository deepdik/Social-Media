from django.contrib import admin
from .models import *


class UserAdmin(admin.ModelAdmin):
	list_display = ('first_name','last_name','mobile_number','email')
	search_fields = ('first_name','last_name','mobile_number','email')


admin.site.register(User, UserAdmin)
admin.site.register([ViewingAndViewers, Ethnicity,UserInterest,Languages, UserPersonalView, UserWorkExperience, UserContactInfo, UserInterests, UserEducationalDetails, SocialLink])
