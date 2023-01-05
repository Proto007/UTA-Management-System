import requests
from django.shortcuts import render

def homepage(request):
    """
    Render homepage.html in default endpoint
    """
    response = requests.post("http://127.0.0.1:8000/api/6d975d9e9f5e6d5a461ded16097ec288/", json={})
    data = response.json()
    return render(request,'homepage.html', {'data':data})
