# basic URL Configurations
from django.urls import include, path
# import routers
from rest_framework import routers

# import everything from views
from .views import *

# define the router
router = routers.DefaultRouter()

# specify URL Path for rest_framework
urlpatterns = [
    path('', include(router.urls)),
    path('messages/', write_message),
    path('users/', get_all_users),
]
