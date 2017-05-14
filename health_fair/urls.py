from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from screener.views import *


urlpatterns = [
    url(r'^dj-admin/', admin.site.urls),
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^search/(?P<slug>[a-zA-Z0-9-]+)$', ScreenView.as_view(), name='screen'),
    url(r'^detail/(?P<npi>[a-zA-Z0-9-]+)$', ProviderDetailView.as_view(), name='detail'),
    url(r'^send-text/(?P<slug>[a-zA-Z0-9-]+)$', SendTextView.as_view(), name='send_text'),
    url(r'^dashboard$', DashboardView.as_view(), name='dashboard')
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
