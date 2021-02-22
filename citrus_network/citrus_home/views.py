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
import requests
import re

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
            citrusAuthor = CitrusAuthor.objects.create(type="author",id=str(uuid.uuid4()), user=user,displayName=user.username)
            citrusAuthor.save()
            return redirect(home_redirect) 
    
    # return form with user input if not valid
    else:
        form = UserCreationForm()
    return render(request, 'citrus_home/register.html', {'form': form})

"""
handles get requests with id and retrieve author profile information: username, displayname, github
handles post requests to state changes to author profile information: username, displayname, github 
Expected: POST - POST body = {"username": "new_username", "displayName": "new_displayName", "github":"new_github"} 
URL:/service/author/{AUTHOR_ID}
"""
def manage_profile(request, id):
    if request.method == 'GET':
        profile = get_object_or_404(CitrusAuthor, id=id)
        current_profile = { 'username': profile.user,
                            'displayName': profile.displayName,
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
            profile = get_object_or_404(CitrusAuthor, id=id)
            profile.user.username = new_username
            profile.displayName = new_displayName
            profile.github = new_github
            profile.user.save()
            profile.save()

            response = JsonResponse({
                "message": "profile updated!"
            })
            response.status_code = 200
            return HttpResponseRedirect(reverse('profile',  kwargs={ 'id': str(profile.id) }))

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

"""
retrieve github username from github url 
"""
def sanitize_git_url(git_url):
    git_username = re.sub('http://github.com/|https://github.com/|https://www.github.com/|http://www.github.com/', '', git_url)
    return git_username

"""
handles get request and list events for the github username 
Expected: 
URL:/service/author/{AUTHOR_ID}/github
reference: https://towardsdatascience.com/build-a-python-crawler-to-get-activity-stream-with-github-api-d1e9f5831d88
"""
def get_github_events(request, id):
    if request.method == 'GET':
        # look up user by their id, if not exist, return 404 response
        profile = get_object_or_404(CitrusAuthor, id=id)
        
        #sanitize github url to get github username
        git_username = sanitize_git_url(profile.github)

        response = requests.get('https://api.github.com/users/{username}/events'.format(username=git_username))

        # validate if username exists:
        if response.status_code == 404:
            err_response = JsonResponse({
                "message": "Profile not found"
            })
            err_response.status_code = 404
            return err_response

        # process data to customized json response
        data = response.json()
        results = []
        
        event_actions = {
            'WatchEvent': 'starred', 
            'PushEvent': 'pushed to', 
            'CreateEvent': "created", 
            'DeleteEvent':'deleted',
            'ForkEvent':'forked',
            'CommitCommentEvent':'committed comment on',
            'IssueCommentEvent': 'issued comment on',
            'IssueEvent': 'issued event on',
            'PullRequestEvent': 'made a pull request on',
            'PullRequestReviewEvent': 'reviewed a pull request on',
            'ReleaseEvent': 'made a realease on'
        }
        
        for event in data:
            if event['type'] in event_actions:
                name = event['actor']['display_login']
                action = event_actions[event['type']] 
                repo = event['repo']['name']
                time = event['created_at']
                action_str = {
                    'type':event['type'],
                    'name':name,
                    'action':action,
                    'repo':repo,
                    'time':time,
                }
                results.append(action_str)
            if event['type'] == 'ForkEvent':
                name = event['actor']['display_login']
                repo = event['repo']['name']  
                forked_repo = event['payload']['forkee']['full_name'] 
                time = event['created_at']
                action_str = {
                    'type':event['type'],
                    'name':name,
                    'action':action,
                    'forked_repo':forked_repo,
                    'repo':repo,
                    'time':time,
                }
                results.append(action_str)
        response = JsonResponse({'events':results})
        response.status_code = 200
        return response

