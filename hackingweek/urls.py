from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView

from django.contrib import admin

import hackingweek.views


urlpatterns = patterns("",
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),
    url(r"^teams/$", TemplateView.as_view(template_name="teams.html"), name="teams"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/settings/$", hackingweek.views.SettingsView.as_view(), name="account_settings"),
    url(r"^account/signup/$", hackingweek.views.SignupView.as_view(), name="account_signup"),
    url(r"^account/", include("account.urls")),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
