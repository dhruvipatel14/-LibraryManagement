from django.urls import path

from .views import Login, UserView

urlpatterns = [
    path("authenticate", Login.as_view()),
    path("registration", UserView.as_view()),
]
