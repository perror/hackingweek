from django.contrib import admin

import models
from hackingweek.forms import ChallengeForm


class CategoryAdmin(admin.ModelAdmin):
     list_display = ['name']
     list_filter  = ('name',)

admin.site.register(models.Category, CategoryAdmin)


class ValidationAdmin(admin.ModelAdmin):
     list_display = ['date', 'user', 'team', 'challenge']
     list_filter  = ('date',)

admin.site.register(models.Validation, ValidationAdmin)


class ChallengeAdmin(admin.ModelAdmin):
     form = ChallengeForm
     list_display = ['name', 'category', 'author', 'body', 'key']
     list_filter  = ('name', 'category')

admin.site.register(models.Challenge, ChallengeAdmin)


class TeamAdmin(admin.ModelAdmin):
     list_display = ['name', 'is_active']
     list_filter  = ('name', 'is_active')

admin.site.register(models.Team, TeamAdmin)


class UserProfileAdmin(admin.ModelAdmin):
     list_display = ['user', 'real_name', 'school', 'study_level']
     list_filter  = ('user',)

admin.site.register(models.UserProfile, UserProfileAdmin)
