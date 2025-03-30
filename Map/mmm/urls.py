from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate_account'),
    path('map/', map_view, name='map'),
    path('scene/', scene_view, name='scene'),
    path("geojson/", geojson_vid, name="geojson_vid"),
    path("trips/", trips, name="trips"),
    path('scene/', scene, name='scene')
]
