from django.urls import path
from rest_framework_simplejwt.views import (TokenBlacklistView,
                                            TokenObtainPairView,
                                            TokenRefreshView)

from authentication import views

urlpatterns = [
    path("register/", views.register_user),
    path("login/", TokenObtainPairView.as_view()),
    path("login/refresh/", TokenRefreshView.as_view()),
    path("logout/", TokenBlacklistView.as_view()),
    path("update/", views.update_user),
    path("update/<int:pk>", views.update_user),
    path("info/", views.get_user_info),
    path("info/<int:pk>", views.get_user_info),
]
