from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib.auth.decorators import login_required
from django.contrib import admin

from django.views.generic import ListView
from django.views.generic import TemplateView

import hackingweek.views

from hackingweek.models import Team
from hackingweek.views import TeamListView, TeamCreateView, TeamQuitView, ContestantListView

from hackingweek.decorators import has_no_team_required, has_team_required

urlpatterns = patterns("",
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),
    url(r"^about/$", TemplateView.as_view(template_name="about.html"), name="about"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/settings/$", hackingweek.views.SettingsView.as_view(), name="account_settings"),
    url(r"^account/signup/$", hackingweek.views.SignupView.as_view(), name="account_signup"),
    url(r"^account/", include("account.urls")),
    url(r"^contestant/list/$", ContestantListView.as_view(template_name="contestant-list.html"), name="contestant_list"),
    url(r"^team/list/$", TeamListView.as_view(template_name="team-list.html"), name="team_list"),
    url(r"^team/create/$", has_no_team_required(TeamCreateView.as_view(template_name="team-create.html")), name="team_create"),
    url(r"^team/join/$", has_no_team_required(TemplateView.as_view(template_name="team-join.html")), name="team_join"),
    url(r"^team/quit/(?P<pk>\d+)/$", has_team_required(TeamQuitView.as_view(template_name="team-quit.html")), name="team_quit"),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
