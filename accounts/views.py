# Agregar a tu accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount import app_settings

def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    form = CustomAuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            name = user.first_name if user.first_name else user.email
            messages.success(request, f"¡Bienvenido de nuevo, {name}!")
            return redirect("core:home")
        else:
            # Errores generales
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, error)
            if not messages.get_messages(request):
                messages.error(request, "Por favor, verifica tus credenciales.")

    # Verificar si Google OAuth está configurado
    google_app_configured = SocialApp.objects.filter(provider='google').exists()
    
    context = {
        "form": form,
        "google_configured": google_app_configured
    }
    return render(request, "login.html", context)

def register_view(request):
    if request.user.is_authenticated:
        return redirect("home") 

    form = CustomUserCreationForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)
            name = user.first_name if user.first_name else user.email
            messages.success(request, f"¡Tu cuenta ha sido creada con éxito! Bienvenido, {name}!")
            return redirect("core:home")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{form.fields[field].label}: {error}")

    return render(request, "register.html", {"form": form})

def signout(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("accounts:login")