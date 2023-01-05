import requests
from django.shortcuts import render

def homepage(request):
    """
    Render homepage.html in default endpoint
    """
    return render(request,'homepage.html')

def getpass(request):
    response = requests.post("http://127.0.0.1:8000/api/6d975d9e9f5e6d5a461ded16097ec288/", json={})
    data = response.json()
    return render(request,'getpass.html', {'data':data})

def checkin(request, random_pass):
    response = requests.post("http://127.0.0.1:8000/api/6d975d9e9f5e6d5a461ded16097ec288/", json={})
    data = response.json()
    new_pass = data['random_pass']
    if random_pass == new_pass:
        return render(request,'checkin.html')
    return render(request, 'homepage.html')
