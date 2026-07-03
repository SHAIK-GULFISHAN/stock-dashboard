from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
from portfolio.views import logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('portfolio/', include('portfolio.urls')),
]