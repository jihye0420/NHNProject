from django.urls import path, include
from rest_framework import routers

from . import views

# router = routers.SimpleRouter()
# router.register('group', views.PostViewSet, basename='Post')

# urlpatterns = router.urls
urlpatterns = [
    path('', views.test),
    path('group/10', views.PostView.as_view()),  # 게시물
#     path('', include(router.urls)),
]
