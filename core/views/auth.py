from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
def custom_logout(request):
    if request.method in ['POST', 'GET']:
        logout(request)
    return redirect('login')
