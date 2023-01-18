from django.urls import path

from . import views

urlpatterns = [
    path('', views.test),
    path('group/', views.PostView.as_view()),  # 게시물
]
