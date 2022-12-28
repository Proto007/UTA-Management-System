from django.http import HttpResponse
from django.shortcuts import render

def homepage(request):
    """
    Render homepage.html in default endpoint
    """
    return render(request,'homepage.html')
