from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import CitrusUser
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate
from django.http.response import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from http import HTTPStatus
from .profile_form import ProfileForm
from django.urls import reverse


def index(request):
    print(request.method)
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

def home_redirect(request):
    return render(request, 'citrus_home/index.html')



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


"""
handles get requests with author_id and retrieve author profile information: username, displayname, github 
URL:/service/author/{AUTHOR_ID}
"""
def get_profile(request, id):
    profile = get_object_or_404(CitrusUser, id=id)
    return render(request, 'citrus_home/profile.html',{'user': profile})

"""
handles post requests with author_id and state changes to author profile information: username, displayname, github 
URL:/service/author/{AUTHOR_ID}
"""
def post_profile(request,id):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # NEED TO SANITIZE DATA AND CHECK FOR UNCHANGED INPUT
        new_username = request.POST.get('username')
        new_displayName = request.POST.get('displayName')
        new_github = request.POST.get('github')

        print(new_username,new_displayName,new_github)

        try:
            profile = get_object_or_404(CitrusUser, id=id)
            profile.username = new_username
            profile.displayName = new_displayName
            profile.github = new_github

            profile.save()

            response = JsonResponse({
                "message": "profile updated!"
            })
            response.status_code = 200
            return HttpResponseRedirect(reverse('profile',  kwargs={ 'id': str(profile.id) }))

        except (KeyError, CitrusUser.DoesNotExist):
            # Redisplay the question voting form.
            response = JsonResponse({
                "message": "couldn't update profile"
            })
            # TODO: find status code
            response.status_code = 418
            return response
    else:
        profile = get_object_or_404(CitrusUser, id=id)
        current_profile = { 'username': profile.username,
                            'displayName': profile.displayName,
                            'github': profile.github}
        form = ProfileForm(current_profile)
    return render(request, 'citrus_home/edit_profile.html', {'form': form, 'user': profile})
