# playstation/urls.py
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from playstation import views

urlpatterns = [
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^accounts/update/$', views.UpdatePlayStationProfileView.as_view(), name='update_account'),
    url(r'^$', views.IndexView.as_view(), name='home'),
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    url(r'^g/$', views.GamePageView.as_view(), name='game'),
    # url(r'^dashboard$', views.IndexView.as_view(), name='dashboard'),
    # url(r'^u/$', views.UserSearchView.as_view(), name='user_search'),
    # url(r'^u/(?P<username>\w+)/$', views.UserSearchView.as_view(), name='user_found'),
]