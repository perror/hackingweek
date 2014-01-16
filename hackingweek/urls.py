from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.views.generic import ListView
from django.views.generic import TemplateView

from django.contrib import admin

import hackingweek.views

from hackingweek.models import Team
from hackingweek.views import TeamCreate, TeamListView, UserListView

urlpatterns = patterns("",
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),
    url(r"^about/$", TemplateView.as_view(template_name="about.html"), name="about"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/settings/$", hackingweek.views.SettingsView.as_view(), name="account_settings"),
    url(r"^account/signup/$", hackingweek.views.SignupView.as_view(), name="account_signup"),
    url(r"^account/", include("account.urls")),
    url(r"^contestants/list/$", UserListView.as_view(template_name="contestants-list.html"), name="contestants_list"),
    url(r"^teams/list/$", TeamListView.as_view(template_name="teams-list.html"), name="teams_list"),
    url(r"^teams/create/$", TeamCreate.as_view(template_name="teams-create.html"), name="teams_create"),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
