from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
from portfolio.views import logout_view, portfolio

urlpatterns = [
    path("admin/", admin.site.urls),

    # Home page
    path("", portfolio, name="home"),

    # Portfolio
    path("portfolio/", include("portfolio.urls")),

    # Login / Logout
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", logout_view, name="logout"),
]