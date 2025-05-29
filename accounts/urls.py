from django.urls import path
from accounts import views

app_name = 'accounts' 

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.signout, name='logout'),
    path('social/cancelled/', views.social_login_cancelled, name='social_login_cancelled'),
    
    # URLs para recuperación de contraseña
    path('password/reset/', views.password_reset_request, name='password_reset_request'),
    path('password/reset/verify/', views.password_reset_verify, name='password_reset_verify'),
    path('password/reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
]