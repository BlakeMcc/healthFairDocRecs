from django.conf.urls import url
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
    url(r'^send-text/(?P<slug>[a-zA-Z0-9-]+)$', SendTextView.as_view(), name='send_text')
]
