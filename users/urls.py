from django.urls import path

from users.views import CreateUserView, UserDetailView, AuthenticateView, index


urlpatterns = [
    path('users', CreateUserView.as_view()),
    path('users/<int:pk>', UserDetailView.as_view()),
    path('login', AuthenticateView.as_view()),
    path('', index),
]
