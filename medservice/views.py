from django.shortcuts import redirect
from django.urls import reverse


def redirect_to_medforms(request):
    return redirect(reverse('home'))
