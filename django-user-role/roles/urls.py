from django.urls import path

from roles import views

urlpatterns = [
    path("createUser/", views.CreateUserView.as_view(), name="create_user"),
    path("createRole/", views.RoleView.as_view(), name="role"),
]
