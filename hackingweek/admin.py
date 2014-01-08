import models

from django.contrib import admin


class UserProfileAdmin(admin.ModelAdmin):
     list_display = ['user', 'real_name', 'school', 'study_level']
     list_filter = ('user',)

admin.site.register(models.UserProfile, UserProfileAdmin)


class TeamAdmin(admin.ModelAdmin):
     list_display = ['name']

admin.site.register(models.Team, TeamAdmin)
