from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^admin/', admin.site.urls,name="admin"),
    url(r'^accounts/', include('allauth.urls')),
]

urlpatterns += staticfiles_urlpatterns()