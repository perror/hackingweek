import models

from django.contrib import admin


class ChallengeAdmin(admin.ModelAdmin):
     list_display = ['name', 'author', 'description', 'password']
     list_filter = ('name',)

admin.site.register(models.Challenge, ChallengeAdmin)


class TeamAdmin(admin.ModelAdmin):
     list_display = ['name']
     list_filter = ('name',)

admin.site.register(models.Team, TeamAdmin)


class UserProfileAdmin(admin.ModelAdmin):
     list_display = ['user', 'real_name', 'school', 'study_level']
     list_filter = ('user',)

admin.site.register(models.UserProfile, UserProfileAdmin)
