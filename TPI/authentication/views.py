from django.shortcuts import redirect, render, HttpResponse

def login(request):
    #if request.user.is_authenticated:
    #    return redirect('/yt/profile/')
    return render(request, 'authentication/login.html')
