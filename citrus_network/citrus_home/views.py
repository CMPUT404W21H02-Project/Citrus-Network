from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import CitrusAuthor
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate, login, logout
from django.http.response import JsonResponse
from http import HTTPStatus
from django.contrib.auth.models import User


def home_redirect(request):
    return render(request, 'citrus_home/index.html')


def login_redirect(request):
    if request.method == "POST":
        print("here")
        username = request.POST.get('username')
        password = request.POST.get('password')
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=username, password=password)
            # login the current user
            login(request,user)
            # print out the ID of the current user
            print("ID: ",request.user.id)
            logout(request)
            return redirect(home_redirect)

        # if the user is not authenticated return the same html page 
        else:
            return render(request, 'citrus_home/login.html', {'form':form})

    form = AuthenticationForm()
    return render(request, 'citrus_home/login.html', {'form':form})


def register_redirect(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # creates the user object
            user = form.save()
            # login with newly created user
            username = request.POST.get('username')
            password = request.POST.get('password')
            # create CitrusAuthor
            citrusAuthor = CitrusAuthor.objects.create(user_type="author",author_id=str(user.id), user=user)
            citrusAuthor.save()
            return redirect(home_redirect) 
    
    # return form with user input if not valid
    else:
        form = UserCreationForm()
    return render(request, 'citrus_home/register.html', {'form': form})
