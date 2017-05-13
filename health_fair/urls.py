from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^dj-admin/', admin.site.urls),
    url(r'$', TemplateView.as_view(template_name='home.html'), name='home'),
]
