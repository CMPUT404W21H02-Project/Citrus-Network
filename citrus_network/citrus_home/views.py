from django.shortcuts import render, redirect, get_object_or_404
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
from django.http import HttpResponse, HttpResponseRedirect
from http import HTTPStatus
from .profile_form import ProfileForm
from django.urls import reverse
from django.contrib.auth.models import User
import uuid

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
            citrusAuthor = CitrusAuthor.objects.create(user_type="author",author_id=str(uuid.uuid4()), user=user,display_name=str(user.username))
            citrusAuthor.save()
            return redirect(home_redirect) 
    
    # return form with user input if not valid
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


"""
handles get requests with author_id and retrieve author profile information: username, displayname, github
handles post requests to state changes to author profile information: username, displayname, github 
Expected: POST - POST body = {"username": "new_username", "displayName": "new_displayName", "github":"new_github"} 
URL:/service/author/{AUTHOR_ID}
"""
def manage_profile(request, id):
    if request.method == 'GET':
        profile = get_object_or_404(CitrusAuthor, author_id=id)
        current_profile = { 'username': profile.user,
                            'displayName': profile.display_name,
                            'github': profile.github}
        form = ProfileForm(current_profile)

        return render(request, 'citrus_home/profile.html',{'form': form, 'user': profile})
    
    # if this is a POST request we need to process the form data
    elif request.method == 'POST':
        # NEED TO SANITIZE DATA AND CHECK FOR UNCHANGED INPUT
        new_username = request.POST.get('username')
        new_displayName = request.POST.get('displayName')
        new_github = request.POST.get('github')

        try:
            profile = get_object_or_404(CitrusAuthor, author_id=id)
            profile.user.username = new_username
            profile.display_name = new_displayName
            profile.github = new_github
            profile.user.save()
            profile.save()

            response = JsonResponse({
                "message": "profile updated!"
            })
            response.status_code = 200
            return HttpResponseRedirect(reverse('profile',  kwargs={ 'id': str(profile.author_id) }))

        except (KeyError, CitrusAuthor.DoesNotExist):
            response = JsonResponse({
                "message": "couldn't update profile"
            })
            response.status_code = 418
            return response
    #not POST AND GET SO return sth else 
    else:
        response = JsonResponse({
            "message": "Method Not Allowed. Only support GET and POST"
        })

        response.status_code = 405
        return response

# def post_profile(request,id):
#     # if this is a POST request we need to process the form data
#     if request.method == 'POST':
#         # NEED TO SANITIZE DATA AND CHECK FOR UNCHANGED INPUT
#         new_username = request.POST.get('username')
#         new_displayName = request.POST.get('displayName')
#         new_github = request.POST.get('github')

#         print(new_username,new_displayName,new_github)

#         try:
#             profile = get_object_or_404(CitrusUser, id=id)
#             profile.username = new_username
#             profile.displayName = new_displayName
#             profile.github = new_github

#             profile.save()

#             response = JsonResponse({
#                 "message": "profile updated!"
#             })
#             response.status_code = 200
#             return HttpResponseRedirect(reverse('profile',  kwargs={ 'id': str(profile.id) }))

#         except (KeyError, CitrusUser.DoesNotExist):
#             # Redisplay the question voting form.
#             response = JsonResponse({
#                 "message": "couldn't update profile"
#             })
#             # TODO: find status code
#             response.status_code = 418
#             return response
#     else:
#         profile = get_object_or_404(CitrusUser, id=id)
#         current_profile = { 'username': profile.username,
#                             'displayName': profile.displayName,
#                             'github': profile.github}
#         form = ProfileForm(current_profile)
#     return render(request, 'citrus_home/edit_profile.html', {'form': form, 'user': profile})
