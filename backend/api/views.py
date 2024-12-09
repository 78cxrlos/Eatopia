from django.shortcuts import render

def base(response):
    return render(response, 'base.html')

def home(request):
    return render(request, 'home.html', {})
