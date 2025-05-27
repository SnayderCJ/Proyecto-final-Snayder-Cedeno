from django.shortcuts import render, redirect
from .forms import SettingsForm
from .models import UserSettings
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    return render(request, 'pages/home.html')

def perfil(request):
    return render(request, 'pages/perfil.html')

def settings(request):
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            user_settings.language = form.cleaned_data['language']
            user_settings.timezone = form.cleaned_data['timezone']
            user_settings.save()
            return redirect('core:settings')  # Redirige a la misma vista o donde desees
    else:
        form = SettingsForm(initial={
            'language': user_settings.language,
            'timezone': user_settings.timezone
        })

    return render(request, 'pages/settings.html', {'form': form})