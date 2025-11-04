from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    
    # Login
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    
    # Logout - AGREGAR ESTA LÍNEA
    path('logout/', auth_views.LogoutView.as_view(
        template_name='registration/logged_out.html'
    ), name='logout'),
    
    path('', RedirectView.as_view(url='/login/')),
]