from django.shortcuts import render
from allauth.socialaccount.models import SocialAccount

# Create your views here.

def home(request):
    return render(request, 'pages/home.html')

def perfil(request):
    google_account = None
    google_avatar = None
    is_google_user = False

    if request.user.is_authenticated:
        google_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
        if google_account:
            is_google_user = True
            google_avatar = google_account.extra_data.get('picture')

    context = {
        'is_google_user': is_google_user,
        'google_avatar': google_avatar,
    }
    return render(request, 'pages/perfil.html', context)