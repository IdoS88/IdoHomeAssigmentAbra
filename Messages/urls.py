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
    path('messages/', CreateListMessageView.as_view()),
    path('messages/0', ListUnreadMessageView.as_view()),
    path('messages/<uuid:message_id>', RetrieveMessageDetailsView.as_view()),
    path('messages/<uuid:message_id>/delete', DeleteMessageDetailsView.as_view()),
    # path('messages/<int:user_id>/',UnReadMessageList.as_view())

]
