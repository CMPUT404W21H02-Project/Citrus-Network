from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import CitrusUser
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate
from django.http.response import JsonResponse
from http import HTTPStatus

def index(request):
    # TODO: render login.html if user is not logged in.
    # Render user home page if user is logged in.
    return redirect(login_redirect)

def home_redirect(request):
    return render(request, 'citrus_home/index.html')

def login_redirect(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if (form.is_valid()):
            response.status_code = 200
            return redirect(home_redirect)
        else:
            return render(request, 'citrus_home/login.html', {'form':form})
    form = AuthenticationForm()
    return render(request, 'citrus_home/login.html', {'form':form})

def register_redirect(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = CitrusUser.objects.create_user(username=username, password=password)
            user.save()
            response = JsonResponse({
                "message": "user created!"
            })
            response.status_code = 200
            return redirect(home_redirect)
        except:
            print('inside except')
            response = JsonResponse({
                "message": "citrus user not created username probably taken"
            })
            # TODO: find status code
            response.status_code = 418
            return response 
    else:
        form = UserCreationForm()
    return render(request, 'citrus_home/register.html', {'form': form})

"""
handles post requests and checks for a username and password, if the username is not taken then a citrus user is created.
Expected: POST - POST body = {"username": "some_usrname", "password": "some_password"}
"""
@csrf_exempt 
def test_sign_up(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = CitrusUser.objects.create_user(username=username, password=password)
            user.save()
            response = JsonResponse({
                "message": "user created!"
            })
            response.status_code = 200
            return response
        except:
            print('inside except')
            response = JsonResponse({
                "message": "citrus user not created username probably taken"
            })
            # TODO: find status code
            response.status_code = 418
            return response