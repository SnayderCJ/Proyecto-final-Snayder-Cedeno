from django.urls import path, include
from views import Home

app_name = "security"

urlpatterns = [
      path('', Home, name='home'),
]