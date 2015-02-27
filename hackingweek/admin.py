from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

import models

from hackingweek.forms import ChallengeForm
from hackingweek.models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


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
