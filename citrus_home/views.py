from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import PostForm
from .models import CitrusAuthor, Friend, Follower, Comment, Post, Inbox, Like, Node
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate, login, logout
from django.http.response import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from http import HTTPStatus
from .profile_form import ProfileForm, ProfileFormError
from django.urls import reverse
import uuid
import requests
import re
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
import ast
import base64
from functools import reduce
import operator
from django.db.models import Q
from urllib.parse import urlparse
from requests.auth import HTTPBasicAuth
# separator of uuids in list of followers and friends
CONST_SEPARATOR = " "

# Follows basic auth scheme where the user:password is sent as a base64 encoding.
# Username is CitrusNetwork and Password is oranges
# https://stackoverflow.com/questions/46426683/django-basic-auth-for-one-view-avoid-middleware
def basicAuthHandler(request):
    
    try:
        current_user = CitrusAuthor.objects.get(user=request.user)
        return True
    except:
        None
    try:
        src = request.META["HTTP_REFERER"]
        parsed = urlparse(src)
        url = parsed.scheme + "://" +parsed.netloc + "/"
        print(url)
        node = Node.objects.get(host=url)
        print(node)
        
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')

        credentials = base64.b64decode(credentials)
        username, password = credentials.decode('utf-8').split(':')
        if username == node.host_username and password == node.host_password and token_type == "Basic":
            return True
        return False
    except:
        return False

def get_team_3_user():
    node = Node.objects.get(host = "https://team3-socialdistribution.herokuapp.com/")
    print("************************************************")
    print(node)
    return node.node_username

def get_team_3_password():
    node = Node.objects.get(host = "https://team3-socialdistribution.herokuapp.com/")
    return node.node_password

def get_team_18_user():
    node = Node.objects.get(host = "https://cmput-404-socialdistribution.herokuapp.com/")
    return node.node_username

def get_team_18_password():
    node = Node.objects.get(host = "https://cmput-404-socialdistribution.herokuapp.com/")
    return node.node_password



@login_required(login_url='login_url')
def home_redirect(request):
    if request.method == 'GET':
        # get uuid from logged in user
        uuid = get_uuid(request)
        return render(request, 'citrus_home/stream.html', {'uuid':uuid})

"""
comment
"""
def login_redirect(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=username, password=password)
            # login the current user
            login(request,user)
            return redirect(home_redirect)

        # if the user is not authenticated return the same html page 
        else:
            return render(request, 'citrus_home/login.html', {'form':form})

    # check if user is still logged in then redirect to home page:
    if request.user.is_authenticated:
        return redirect(home_redirect)
    
    form = AuthenticationForm()
    return render(request, 'citrus_home/login.html', {'form':form})

"""
require authorization, log out current user, redirect to the home page
"""
# @login_required
def logout_redirect(request):
    if request.method == "GET":
        logout(request)   
        return redirect(login_redirect)

"""
comment
"""
def register_redirect(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # creates the user object
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            # login with newly created user
            username = request.POST.get('username')
            password = request.POST.get('password')
            login(request,user)
            # create CitrusAuthor

            base_host = request.META['HTTP_HOST'] 
            if "http" not in base_host:
                base_host = "http://" + base_host
            if not base_host.endswith("/"):
                base_host += "/"
 
            auth_id =  str(uuid.uuid4())
            url = base_host  +  "author/" + auth_id    
            host = base_host                           
            
            citrusAuthor = CitrusAuthor.objects.create(type="author", 
                                                       id=auth_id , 
                                                       user=user, 
                                                       displayName=user.username, 
                                                       host=host, 
                                                       url=url)


            result = citrusAuthor.save()

            return redirect(home_redirect) 
    
    # return form with user input if not valid
    else:
        form = UserCreationForm()
    return render(request, 'citrus_home/register.html', {'form': form})

"""
get the uuid of a logged in user
"""
@login_required
def get_uuid(request):
    profiles = get_list_or_404(CitrusAuthor,user = request.user.id)
    uuid = profiles[0].id
    return uuid

"""
render edit_profile html page
require authentication by successfully logging in
"""
@login_required(login_url='login_url')
def render_profile(request):
    if request.method == 'POST':
        # get uuid from logged in user
        uuid = get_uuid(request)
        profile = get_object_or_404(CitrusAuthor, id=uuid)

        #new data     
        new_username = request.POST.get('username')
        new_displayName = request.POST.get('displayName')
        new_github = request.POST.get('github')

        # set which fields are valid/invalid for the html
        field_validities = setFormErrors(profile,new_username,new_displayName,new_github)
        pf_form_errors = ProfileFormError(field_validities[0],field_validities[1],field_validities[2])
        try:
            validate_fields(field_validities)
        except forms.ValidationError:
            #if the github, username, or display name exists and was someone elses return the users original information
            current_profile = { 'username': profile.user,'displayName': profile.displayName,'github': profile.github }
            form = ProfileForm(current_profile)

            return render(request, 'citrus_home/profile.html',{'form': form, 'profile': current_profile, 'pf_form_errors':pf_form_errors})
        
        #if fields were valid, assign them to user
        profile.user.username = str(new_username)
        profile.displayName = str(new_displayName)
        profile.github = str(new_github)
        profile.user.save()
        profile.save()

        # set up Django form
        current_profile = { 'username': profile.user,'displayName': profile.displayName,'github': profile.github }
        form = ProfileForm(current_profile)

        response = JsonResponse({
            "message": "profile updated!"
        })
        response.status_code = 200
        # return HttpResponseRedirect(reverse('profile',  kwargs={ 'id': str(profile.id) }))
        return render(request, 'citrus_home/profile.html',{'form': form, 'profile': current_profile, 'response':response, 'pf_form_errors':pf_form_errors }) 


    # handle not POST OR GET (to-do)
    uuid = get_uuid(request)
    profile = get_object_or_404(CitrusAuthor, id=uuid)

    current_profile = { 'username': profile.user,
                        'displayName': profile.displayName,
                        'github': profile.github}
    response = JsonResponse({'username': str(profile.user),
                            'displayName': str(profile.displayName),
                            'github': str(profile.github)})
    response.status_code = 200
    form = ProfileForm(current_profile)
    return render(request, 'citrus_home/profile.html',{'form': form, 'profile': current_profile})

"""
render viewprofile html
require authentication by successfully logging in
"""
@login_required(login_url='login_url')
def render_author_profile(request, author_id):
    if request.method == 'GET':
        current_user = CitrusAuthor.objects.get(user=request.user)
        if str(current_user.id) == str(author_id):
            return redirect(render_profile)

        try:
            author = CitrusAuthor.objects.get(id=author_id)
            response = {
                "type": "author",
                "id": author.id,
                "host": author.host,
                "username": author.user,
                "displayName": author.displayName,
                "url": author.url,
                "github": author.github
            }
            return render(request, 'citrus_home/viewprofile.html', {'author': response, 'postsURL': author.host + 'service/author/' + author.id + '/posts/' })
        except ObjectDoesNotExist:
            nodes = Node.objects.all()
            for node in nodes:
                if node.host == 'https://cmput-404-socialdistribution.herokuapp.com/':
                    req = requests.get(node.host + 'service/author/' + str(author_id) + '/')
                    if req.status_code == 200:
                        author = req.json()
                        response = {
                            "type": "author",
                            "id": author["id"].split('/author/')[1],
                            "host": author["host"],
                            "username": author["displayName"],
                            "displayName": author["displayName"],
                            "url": author["url"],
                            "github": author["github"]
                        }
                        return render(request, 'citrus_home/viewprofile.html', {'author': response, 'postsURL': author["host"] + 'service/author/' + response["id"] + '/posts/' })
                elif node.host == 'https://team3-socialdistribution.herokuapp.com/':
                    req = requests.get(node.host + 'author/' + str(author_id) + '/')
                    if req.status_code == 200:
                        author = req.json()
                        response = {
                            "type": "author",
                            "id": author["id"],
                            "host": author["host"],
                            "username": author["displayName"],
                            "displayName": author["displayName"],
                            "url": author["url"],
                            "github": author["github"]
                        }
                        return render(request, 'citrus_home/viewprofile.html', {'author': response, 'postsURL': author["host"] + 'author/' + response["id"] + '/posts/' })

def get_authors_public_posts(request, author_id):
    if not basicAuthHandler(request):
        response = JsonResponse({'message':'not authenticated'})
        response.status_code = 401
        return response

    if request.method == 'GET':
        try:
            author = CitrusAuthor.objects.get(id=author_id)
            req = requests.get(author.host + 'service/author/' + str(author.id) + '/posts/')
            # print(req)
            return JsonResponse(req.json())
        except ObjectDoesNotExist:
            nodes = Node.objects.all()
            for node in nodes:
                if node.host == 'https://cmput-404-socialdistribution.herokuapp.com/':
                    req = requests.get(node.host + 'service/author/' + str(author_id) + '/')
                    if req.status_code == 200:
                        req = requests.get(node.host + 'service/author/' + str(author_id) + '/posts/').json()
                        # print('team 18', req)
                        for i in req["posts"]:
                            i["id"] = i["postID"]
                            i["author"]["id"] = i["authorID"]
                        return JsonResponse(req)
                elif node.host == 'https://team3-socialdistribution.herokuapp.com/':
                    req = requests.get(node.host + 'author/' + str(author_id) + '/')
                    if req.status_code == 200:
                        req = requests.get(node.host + 'author/' + str(author_id) + '/posts/')
                        return JsonResponse({"posts":req.json()})

"""
handles get requests with id and retrieve author profile information: username, displayname, github
handles post requests to state changes to author profile information: username, displayname, github 
Expected: POST - POST body = {"username": "new_username", "displayName": "new_displayName", "github":"new_github"} 
URL:/service/author/{AUTHOR_ID}
"""
# @login_required
def manage_profile(request, id):
    if not basicAuthHandler(request):
        response = JsonResponse({'message':'not authenticated'})
        response.status_code = 401
        return response
    if request.method == 'GET':
        profile = get_object_or_404(CitrusAuthor, id=id)

        response = JsonResponse({'type' : str(profile.type),
                                 'id': str(profile.id),
                                 'host' : str(profile.host),
                                 'username' : str(profile.user),
                                 'displayName' : str(profile.displayName),
                                 'url': str(profile.url),
                                 'github': str(profile.github)})

        response.status_code = 200
        return response
        
    # if this is a POST request we need to process the form data
    elif request.method == 'POST':
        # NEED TO SANITIZE DATA AND CHECK FOR UNCHANGED INPUT
        
        new_username = request.POST.get('username')
        new_displayName = request.POST.get('displayName')
        new_github = request.POST.get('github')

        try:
            profile = get_object_or_404(CitrusAuthor, id=id)

            # set which fields are valid/invalid for the html
            field_validities = setFormErrors(profile,new_username,new_displayName,new_github)
            pf_form_errors = ProfileFormError(field_validities[0],field_validities[1],field_validities[2])
            try:
                validate_fields(field_validities)
            except forms.ValidationError:
                #if the github, username, or display name exists and was someone elses return the users original information
                response = JsonResponse({
                    "message": "couldn't update profile"
                })
                response.status_code = 400
                return response
            
            #if fields were valid, assign them to user
            profile.user.username = new_username
            profile.displayName = new_displayName
            profile.github = new_github
            profile.user.save()
            profile.save()

            response = JsonResponse({
                "message": "profile updated!"
            })
            response.status_code = 200
            return response

        except (KeyError, CitrusAuthor.DoesNotExist):
            response = JsonResponse({
                "message": "couldn't update profile"
            })
            response.status_code = 500
            return response
    #not POST AND GET SO return sth else 
    else:
        response = JsonResponse({
            "message": "Method Not Allowed. Only support GET and POST"
        })

        response.status_code = 405
        return response

'''
Helper function to get the booleans that will be used to 
set custom form errors for the user editing their profile
PARAMS: profile - current users information,
        new_username - requested new username,
        new_displayName - requested new display name,
        new_github - requested new github.
RETURN: list of three booleans
'''
def setFormErrors(profile,new_username,new_displayName,new_github):
    u_valid = validate_username(profile, new_username)
    d_valid = validate_displayName(profile,new_displayName)
    g_valid = validate_github(profile,new_github)
    
    return [u_valid,d_valid,g_valid] 
'''
Helper function that raises and error if one of the fields is not available
PARAMS: field validites - a list of booleans
'''
def validate_fields(field_validities):
    print(field_validities)
    if False in field_validities:
        raise forms.ValidationError(u'one of three fields  are already in use.')
    else:
        return

'''
Function to validate a requested username
PARAMS: profile - current users profile,
        new_username - requested username
RETURN: boolean - True if available, False if unavailable
'''
def validate_username(profile, new_username):
    #cant query for username attributes from Citrus Author object
    if User.objects.filter(username=new_username).exists():
        existing_user = User.objects.get(username=new_username) 
        if  existing_user.id != profile.user.id:
            return False
        else:
            return True
    else:
        return True

'''
Function to validate a requested displayName
PARAMS: profile - current users profile,
        new_displayName - requested displayName
RETURN: boolean - True if available, False if unavailable
'''
def validate_displayName(profile, new_displayName):  
    if CitrusAuthor.objects.filter(displayName=new_displayName).exists():
        existing_user = CitrusAuthor.objects.get(displayName=new_displayName)
        if existing_user.id != profile.id:
            return False
        else:
            return True
    else:
        return True

'''
Function to validate a requested github
PARAMS: profile - current users profile,
        new_github - requested github
RETURN: boolean - True if available, False if unavailable
'''
def validate_github(profile,  new_github):
    if CitrusAuthor.objects.filter(github=new_github).exists():
        existing_user = CitrusAuthor.objects.get(github=new_github)
        if existing_user.id != profile.id:
            return False
        else:
            return True
    else:
        return True
        
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
# @login_required
def get_github_events(request, id):
    if not basicAuthHandler(request):
        response = JsonResponse({'message':'not authenticated'})
        response.status_code = 401
        return response
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


"""
handles GET request: get a list of authors on the server
Expected: 
URL: ://service/authors
"""
@csrf_exempt
def get_authors(request):
    if not basicAuthHandler(request):
        response = JsonResponse({'message':'not authenticated'})
        response.status_code = 401
        return response
    if request.method == "GET":  
        all_user = CitrusAuthor.objects.all()

        # generate json response for list of not followers
        items = []
        for user in all_user:
            # get the author profile info
            json = {
                "type": "Author",
                "id": str(user.id),
                "host": str(user.host),
                "displayName": str(user.displayName),
                "github": str(user.github),
            }
            items.append(json)

        results = { "type": "author",      
                    "items": items}

        response = JsonResponse(results)
        response.status_code = 200
        return response
    else:
        response = JsonResponse({'message':'method not allowed'})
        response.status_code = 405
        return response

'''
function to check if team 3 server exist in connecting node
RETURN: response
'''
def check_team3_in_node():
    URL_TEAM3 = "https://team3-socialdistribution.herokuapp.com/"
    
    try:
        node_team3 = Node.objects.get(host=URL_TEAM3)
    except ObjectDoesNotExist:
        return False
    return True

'''
function to check if team 18 server exist in connecting node
RETURN: response
'''
def check_team18_in_node():
    URL_TEAM18 = "https://cmput-404-socialdistribution.herokuapp.com/"
    
    try:
        node_team18 = Node.objects.get(host=URL_TEAM18)
    except ObjectDoesNotExist:
        return False
    return True

'''
function to check if author exist in team 3 server
PARAMS: author id
RETURN: response
'''
def check_author_exist_team3(author_id):
    URL_TEAM3 = "https://team3-socialdistribution.herokuapp.com/author/"
    url = URL_TEAM3 + str(author_id)
    response = requests.get(url, auth=HTTPBasicAuth(get_team_3_user(), get_team_3_password()))
    return response

'''
function to check if author exist in team 18 server
PARAMS: author id
RETURN: response
'''
def check_author_exist_team18(author_id):
    URL_TEAM18 = "https://cmput-404-socialdistribution.herokuapp.com/service/author/"
    FORWARD_SLASH = "/"
    url = URL_TEAM18 + str(author_id) + FORWARD_SLASH
    response = requests.get(url, auth=HTTPBasicAuth(get_team_18_user(), get_team_18_password()))
    return response

'''
function to check if author_id is a follower of actor_id from team 18 server
PARAMS: author id
RETURN: response
'''
def check_author_follows_actor_team18(author_id,actor_id):
    URL_TEAM18 = "https://cmput-404-socialdistribution.herokuapp.com/service/author/"
    FOLLOWERS = "followers"
    FORWARD_SLASH = "/"
    url = URL_TEAM18 + str(actor_id) + FORWARD_SLASH + FOLLOWERS + FORWARD_SLASH + str(author_id) + FORWARD_SLASH
    response = requests.get(url, auth=HTTPBasicAuth(get_team_18_user(), get_team_18_password()))
    return response

'''
function to check if author_id is a follower of actor_id from team 3 server
PARAMS: author id
RETURN: response
'''
def check_author_follows_actor_team3(author_id,actor_id):
    URL_TEAM3 = "https://team3-socialdistribution.herokuapp.com/author/"
    FOLLOWERS = "followers"
    FORWARD_SLASH = "/"
    url = URL_TEAM3 + str(actor_id) + FORWARD_SLASH + FOLLOWERS + FORWARD_SLASH + str(author_id) 
    response = requests.get(url, auth=HTTPBasicAuth(get_team_3_user(), get_team_3_password()))
    return response

'''
function to check if author exist in our Citrus Author model 
PARAMS: author id
RETURN: True or False
'''
def check_author_exist_in_CitrusAuthor(author_id):
    try:
        author_id = CitrusAuthor.objects.get(id=author_id)
    except ObjectDoesNotExist:
        return False
    return True

'''
function to check if author exist in our Follower model 
PARAMS: author id
RETURN: True or False
'''
def check_author_exist_in_Follower(author_id):
    try:
        result = Follower.objects.get(uuid=author_id)
    except ObjectDoesNotExist:
        return False
    return True


'''
function to check if author exist in our Friend model 
PARAMS: author id
RETURN: True or False
'''
def check_author_exist_in_Friend(author_id):
    try:
        result = Friend.objects.get(uuid=author_id)
    except ObjectDoesNotExist:
        return False
    return True


'''
function to check if author exists in Friend model
PARAMS: author id
RETURN: True or False
'''
def check_author_exist_in_Friend(author_id):
    try:
        result = Friend.objects.get(uuid=author_id)
    except ObjectDoesNotExist:
        return False
    return True

"""
get a specific authors from team 18 by uuid
Expected: 
"""
def get_team18_author_by_id(uuid):
    URL = "https://cmput-404-socialdistribution.herokuapp.com/service/author/" + uuid +"/"
    response = requests.get(URL, auth=HTTPBasicAuth(get_team_18_user(), get_team_18_password()))
    result = response.json()
    return result

"""
get a specific authors from team 3 by uuid
Expected: 
"""
def get_team3_author_by_id(uuid):
    URL = "https://team3-socialdistribution.herokuapp.com/author/" + uuid
    print(URL)
    response = requests.get(URL, auth=HTTPBasicAuth(get_team_3_user(), get_team_3_password()))
    result = response.json()
    return result

"""
get a list of authors from team 3
Expected: 
"""
def get_team3_authors():
    URL = "https://team3-socialdistribution.herokuapp.com/authors"
    #response = requests.get(URL, auth=HTTPBasicAuth(get_team_3_user(), get_team_3_password()))
    response = requests.get(URL)
    result = response.json()
    print(result)
    return result

"""
get a list of authors from team 18
Expected: 
"""
def get_team18_authors():
    URL = "https://cmput-404-socialdistribution.herokuapp.com/service/author/"
    response = requests.get(URL, auth=HTTPBasicAuth(get_team_18_user(), get_team_18_password()))
    result = response.json()
    return result

"""
handles GET request: get a list of authors who are not their followers or friends
Expected: 
URL: ://service/authors/{AUTHOR_ID}/nonfollowers
"""
@login_required
def get_not_followers(request,author_id):
    if not basicAuthHandler(request):
        response = JsonResponse({'message':'not authenticated'})
        response.status_code = 401
        return response
    if request.method == 'GET':
        author = get_object_or_404(CitrusAuthor, id=author_id)
        
        try: 
            result = Follower.objects.get(uuid = author)
        except ObjectDoesNotExist:
            all_user = CitrusAuthor.objects.all()
            not_followers = []
            
            # adding all user from our server without author_id
            for user in all_user:
                if (str(user.id) != str(author_id)):
                    not_followers.append(user)

            if len(not_followers)==0:
                response = JsonResponse({"results":"no non-followers found"})
                response.status_code = 200
                return response

            # generate json response for list of not followers
            items = []
            for user in not_followers:
                # get the follower profile info
                json = {
                    "type": "Author",
                    "id": str(user.id),
                    "host": str(user.host),
                    "displayName": str(user.displayName),
                    "github": str(user.github),
                }
                items.append(json)
            
            # adding all user from team 3 server
            if check_team3_in_node():
                authors3 = get_team3_authors()
                for author in authors3:
                    items.append(author)
            # adding all user from team 18 server
            if check_team18_in_node():
                authors18 = get_team18_authors() 
                for author in authors18:
                    items.append(author)

            # check to see nothing is in items list
            if len(items) == 0:
                response = JsonResponse({"results":"no non-followers found"})
                response.status_code = 200
                return response

            results = { "type": "non-follower",
                        "items":items}

            response = JsonResponse(results)
            response.status_code = 200
            return response
 

        followers = result.followers_uuid

        all_user = CitrusAuthor.objects.all()

        # get intersection of all_user and followers and disregarding the author_id to return all users author hasn't followed
        not_followers = []
        # check users in our server
        for user in all_user:
            if (str(user.id) not in str(followers) and str(user.id) != str(author_id)):
                not_followers.append(user)

        # generate json response for list of not followers
        items = []

        # check users in team 3 server
        if check_team3_in_node():
            authors3 = get_team3_authors()
            for user in authors3:
                if (str(user['id']) not in str(followers) and str(user['id']) != str(author_id)):
                    items.append(user) # add them into items containing list of non-followers
        # check users in team 18 server
        if check_team18_in_node():
            authors18 = get_team18_authors() 
            for user in authors18:
                if (str(user["authorID"]) not in str(followers) and str(user["authorID"]) != str(author_id)):
                    items.append(user) # add them into items containing list of non-followers
        
        # check to see if list of not_followers from our server and items for non-followers from other server are empty:
        if len(not_followers)==0 and len(items)==0:
            response = JsonResponse({"results":"no non-followers found"})
            response.status_code = 200
            return response

        # add more non follower from our server to items
        for user in not_followers:
            # get the follower profile info
            json = {
                "type": "Author",
                "id": str(user.id),
                "host": str(user.host),
                "displayName": str(user.displayName),
                "github": str(user.github),
            }
            items.append(json)

        # check to see nothing is in items list
        if len(items) == 0:
            response = JsonResponse({"results":"no non-followers found"})
            response.status_code = 200
            return response

        results = { "type": "non-follower",      
                    "items":items}

        response = JsonResponse(results)
        response.status_code = 200
        return response
        
    else:
        response = JsonResponse({'message':'method not allowed'})
        response.status_code = 405
        return response

"""
handles GET request: get a list of authors who are their followers
format of list of followers: uuids separated by CONST_SEPARATOR
Expected: 
URL: ://service/author/{AUTHOR_ID}/followers
"""
def get_followers(request, author_id):
    if not basicAuthHandler(request):
        response = JsonResponse({'message':'not authenticated'})
        response.status_code = 401
        return response
    if request.method == 'GET':
        # check for list of followers of author_id
        try:
            result = Follower.objects.get(uuid=author_id)
        except ObjectDoesNotExist:
            response = JsonResponse({"results":"no followers found or incorrect id of author"})
            response.status_code = 404
            return response

        # generate json response for list of followers
        items = []
        for uuid in result.followers_uuid.split(CONST_SEPARATOR):
            # make sure it is uuid not any blank space
            if uuid:
                uuid = uuid.strip() # remove any whitespace

                # check if uuid is on another server:
                check3 = check_author_exist_team3(uuid)
                check18 = check_author_exist_team18(uuid) 
                if check3.status_code == 200:
                    if check_team3_in_node():
                        items.append(check3.json())
                elif check18.status_code == 200:
                    if check_team18_in_node():
                        items.append(check18.json())
                else: # uuid is in our server
                    # get the follower profile info
                    author = CitrusAuthor.objects.get(id = uuid)
                    
                    json = {
                        "type": "author",
                        "id": str(uuid),
                        "host": str(author.host),
                        "displayName": str(author.displayName),
                        "github": str(author.github),
                    }
                    items.append(json)

        # check to see nothing is in items list
        if len(items) == 0:
            response = JsonResponse({"results":"no followers found or incorrect id of author"})
            response.status_code = 404
            return response

        #LEAH MARCH 4 - THIS IS MISSING AN "S" FROM SPEC lol. change to "type":"followers"
        results = { "type": "followers",      
                    "items":items}

        response = JsonResponse(results)
        response.status_code = 200
        return response
    else:
        response = JsonResponse({"results":"method not allowed"})
        response.status_code = 405
        return response

'''
function to render the followers page
PARAMS: request
RETURN: request, followers page, current user id
'''
def render_followers_page(request):
    uuid = get_uuid(request)
    return render(request,'citrus_home/followers.html', {'uuid':uuid})


"""
handles these requests:
    DELETE: remove a follower, if friend also then unfriend and unfollow that person
    PUT: Add a follower (must be authenticated) or accept friend request to befriend and follow foreign_author_id
    GET check if follower
Expected: 
URL: ://service/author/{AUTHOR_ID}/followers/{FOREIGN_AUTHOR_ID}
"""
@csrf_exempt
def edit_followers(request, author_id, foreign_author_id):
    if not basicAuthHandler(request):
        response = JsonResponse({'message':'not authenticated'})
        response.status_code = 401
        return response
    # special case:
    if author_id == foreign_author_id:
        response = JsonResponse({"message":"author id and foreign author id are the same"})
        response.status_code = 400
        return response        
    elif request.method == 'DELETE':
        # validate author id in model
        print("AH STH")
        try:
            author_obj = CitrusAuthor.objects.get(id=author_id)
            author = Follower.objects.get(uuid=author_obj)
        except ObjectDoesNotExist:
            response = JsonResponse({"results":"author has no followers or incorrect id of author"})
            response.status_code = 404
            return response
        
        # validate foregin id in list of followers:
        followers = str(author.followers_uuid)
        print(followers)
        if str(foreign_author_id) not in followers:
            response = JsonResponse({"results":"foreign id is not a follower"})
            response.status_code = 304
            return response
        
        # unfollow that person
        followers = followers.replace(str(foreign_author_id),"")
        author.followers_uuid = followers
        author.save()

        # check if they're also friend                
        # validate author id in model
        try:
            result = Friend.objects.get(uuid=author_id)
        except ObjectDoesNotExist: # they are not friend because author has no friend
            response = JsonResponse({"results":"unfollow success"})
            response.status_code = 200
            return response        
        # validate foregin id in list of friends:
        friends = str(result.friends_uuid)
        if str(foreign_author_id) not in friends:
            response = JsonResponse({"results":"unfollow success"})
            response.status_code = 200
            return response
        
        # unfriend foreign_author_id
        friends = friends.replace(str(foreign_author_id),"")
        result.friends_uuid = friends
        result.save()

        # unfriend author_id also meaning remove author_id from foreign_author_id friend list 
        # check if this foreign author is from our server or their server
        check_ours = check_author_exist_in_CitrusAuthor(foreign_author_id)
        check18 = check_author_exist_team18(foreign_author_id)
        check3 = check_author_exist_team3(foreign_author_id)

        if check_ours == True:
            foreign_author = Friend.objects.get(uuid=foreign_author_id)
            friends = str(foreign_author.friends_uuid)
            friends = friends.replace(str(author_id),"")
            foreign_author.friends_uuid = friends
            foreign_author.save()
        elif check18.status_code == 200:
            print("DO STH TO REMOVE THIS ON TEAM 18 SERVER")
        elif check3.status_code == 200:
            print("DO STH TO REMOVE THIS ON TEAM 3 SERVER")

        response = JsonResponse({"results":"unfollow and unfriend success"})
        response.status_code = 200
        return response

    elif request.method == 'PUT':
        # validate author id in citrus_author model:
        try:
            author = CitrusAuthor.objects.get(id=author_id)
        except ObjectDoesNotExist: 
            response = JsonResponse({"results":"author_id doesnt exist on server"})                
            response.status_code = 404
            return response

        # validate foregin id in citrus_author model:
        #need to also check here if the author exists in team18 and team3
        if (check_author_exist_in_CitrusAuthor(foreign_author_id) == False):
            response = JsonResponse({"results":"foreign id doesn't exist on our server or team18's"})
            response.status_code = 404
            return response

        # validate author id in follower model
        # uuid need to be a CitrusAuthor instance
        try:
            author = CitrusAuthor.objects.get(id=author_id)
            result = Follower.objects.get(uuid=author)
        except ObjectDoesNotExist:
            followers = str(foreign_author_id)
            # create instance of the follower with uuid to author_id
            new_follower_object = Follower(uuid = author,followers_uuid= followers)
            new_follower_object.save()

            # check if foreign_author_id also follow author_id
            try:
                foreign_author = Follower.objects.get(uuid=foreign_author_id)
            except ObjectDoesNotExist: # foreign_author_id has no followers
                response = JsonResponse({"results":"success"})
                response.status_code = 200
                return response
            else:
                followers = str(foreign_author.followers_uuid)
                # foreign_author_id doesnt follow author_id
                if str(author_id) not in followers:
                    response = JsonResponse({"results":"success"})
                    response.status_code = 200
                    return response

                # foreign_author_id also follow author_id
                # add both of them as friend of each other in Friend model

                # check author_id exist in friend model:
                try:
                    author = CitrusAuthor.objects.get(id=author_id)
                    author_id_friends = Friend.objects.get(uuid=author)
                except ObjectDoesNotExist: # author id is not in friend model
                    # create instance of the follower with uuid to author_id
                    friend = str(foreign_author_id)
                    author = CitrusAuthor.objects.get(id=author_id)
                    new_friend_object = Friend(uuid = author,friends_uuid= friend)
                    new_friend_object.save()
                else:
                    # add foreign id 
                    friends = str(author_id_friends.friends_uuid)+CONST_SEPARATOR+str(foreign_author_id)
                    author_id_friends.friends_uuid = friends
                    author_id_friends.save()

                # check foreign_author_id exist in friend model:
                try:
                    foreign_author = CitrusAuthor.objects.get(id=foreign_author_id)
                    foreign_author_id_friends = Friend.objects.get(uuid=foreign_author)
                except ObjectDoesNotExist: # author id is not in friend model
                    # create instance of the follower with uuid to foreign_author_id
                    friend = str(author_id)
                    foreign_author = CitrusAuthor.objects.get(id=foreign_author_id)
                    new_friend_object = Friend(uuid = foreign_author,friends_uuid= friend)
                    new_friend_object.save()
                else:
                    # add author id 
                    friends = str(foreign_author_id_friends.friends_uuid)+CONST_SEPARATOR+str(author_id)
                    foreign_author_id_friends.friends_uuid = friends
                    foreign_author_id_friends.save()
                    

                response = JsonResponse({"results":"success, added as friends and followers"})
                response.status_code = 200
                return response
        
        # check if foreign id is already a follower
        followers = str(result.followers_uuid)
        if str(foreign_author_id) in followers:
            response = JsonResponse({"results":"foreign id is already a follower"})
            response.status_code = 304
            return response
        
        # add foreign id 
        followers = str(result.followers_uuid)+CONST_SEPARATOR+str(foreign_author_id)
        result.followers_uuid = followers
        result.save()

        # check if foreign_author_id also follow author_id
        try:
            foreign_author = Follower.objects.get(uuid=foreign_author_id)
        except ObjectDoesNotExist: # foreign_author_id has no followers
            response = JsonResponse({"results":"success"})
            response.status_code = 200
            return response
        else:
            followers = str(foreign_author.followers_uuid)
            # foreign_author_id doesnt follow author_id
            if str(author_id) not in followers:
                response = JsonResponse({"results":"success"})
                response.status_code = 200
                return response

            # foreign_author_id also follow author_id
            # add both of them as friend of each other in Friend model

            # check author_id exist in friend model:
            try:
                author_id_friends = Friend.objects.get(uuid=author)
            except ObjectDoesNotExist: # author id is not in friend model
                # create instance of the follower with uuid to author_id
                friend = str(foreign_author_id)
                new_friend_object = Friend(uuid = author,friends_uuid= friend)
                new_friend_object.save()
            else:
                # add foreign id 
                friends = str(author_id_friends.friends_uuid)+CONST_SEPARATOR+str(foreign_author_id)
                author_id_friends.friends_uuid = friends
                author_id_friends.save()

            # check foreign_author_id exist in friend model:
            try:
                foreign_author_id_friends = Friend.objects.get(uuid=foreign_author_id)
            except ObjectDoesNotExist: # author id is not in friend model
                # create instance of the follower with uuid to foreign_author_id
                friend = str(author_id)
                new_friend_object = Friend(uuid = foreign_author_id,friends_uuid= friend)
                new_friend_object.save()
            else:
                # add author id 
                friends = str(foreign_author_id_friends.friends_uuid)+CONST_SEPARATOR+str(author_id)
                foreign_author_id_friends.friends_uuid = friends
                foreign_author_id_friends.save()
                

            response = JsonResponse({"results":"success, added as friends and followers"})
            response.status_code = 200
            return response

        response = JsonResponse({"results":"success, added as friends and followers"})
        response.status_code = 200
        return response

    elif request.method == 'GET':
        # validate author id in model
        try:
            result = Follower.objects.get(uuid=author_id)
        except ObjectDoesNotExist:
            response = JsonResponse({"results":"author has no followers or incorrect id of author"})
            response.status_code = 404
            return response
        
        # validate foregin id in list of followers:
        followers = str(result.followers_uuid)
        if str(foreign_author_id) not in followers:
            response = JsonResponse({"results":"foreign id is not a follower"})
            response.status_code = 404
            return response
        
        response = JsonResponse({"results":"found"})
        response.status_code = 200
        return response
    else:
        response = JsonResponse({"message":"Method not Allowed"})
        response.status_code = 405
        return response

"""
handles these requests:
    GET get all friends
Expected: 
URL: ://service/author/{AUTHOR_ID}/friends/
"""
# @login_required
@csrf_exempt
def get_friends(request, author_id):
    if not basicAuthHandler(request):
        response = JsonResponse({'message':'not authenticated'})
        response.status_code = 401
        return response
    if request.method == 'GET':
        # check for list of followers of author_id
        try:
            author = CitrusAuthor.objects.get(id = author_id)
            result = Friend.objects.get(uuid=author)
        except ObjectDoesNotExist:
            response = JsonResponse({"results":"no friends found or incorrect id of author"})
            response.status_code = 404
            return response


        # generate json response for list of followers
        items = []
        for uuid in result.friends_uuid.split(CONST_SEPARATOR):
            # make sure it is uuid not any blank space
            if uuid:
                uuid = uuid.strip() # remove any whitespace

                # check if uuid is on another server:
                check3 = check_author_exist_team3(uuid)
                check18 = check_author_exist_team18(uuid)
                if check3.status_code == 200:
                    if check_team3_in_node():
                        items.append(check3.json())
                elif check18.status_code == 200:
                    if check_team18_in_node():
                        items.append(check18.json()) 
                else: # uuid is in our server
                    # get the follower profile info
                    author = CitrusAuthor.objects.get(id = uuid)
                    
                    json = {
                        "type": "author",
                        "id": str(uuid),
                        "host": str(author.host),
                        "displayName": str(author.displayName),
                        "github": str(author.github),
                    }
                    items.append(json)

        # check to see nothing is in items list
        if len(items) == 0:
            response = JsonResponse({"results":"no friends found or incorrect id of author"})
            response.status_code = 404
            return response

        results = { "type": "friend",      
                    "items":items}

        response = JsonResponse(results)
        response.status_code = 200
        return response
    else:
        response = JsonResponse({"results":"method not allowed"})
        response.status_code = 405
        return response

"""
handles these requests:
    GET check if friend
    PUT put OTHER SERVER'S AUTHOR_ID into author_id friend list
Expected: 
URL: ://service/author/{AUTHOR_ID}/friends/{FOREIGN_AUTHOR_ID}
"""
# @login_required
@csrf_exempt
def edit_friends(request, author_id, foreign_author_id):
    if not basicAuthHandler(request):
        response = JsonResponse({'message':'not authenticated'})
        response.status_code = 401
        return response
    # special case:
    if author_id == foreign_author_id:
        response = JsonResponse({"message":"author id and foreign author id are the same"})
        response.status_code = 400
        return response        
    elif request.method == 'GET':
        # validate author id in model
        try:
            result = Friend.objects.get(uuid=author_id)
        except ObjectDoesNotExist:
            response = JsonResponse({"results":"author has no friends or incorrect id of author"})
            response.status_code = 404
            return response
        
        # validate foregin id in list of friends:
        friends = str(result.friends_uuid)
        if str(foreign_author_id) not in friends:
            response = JsonResponse({"results":"foreign id is not a friend"})
            response.status_code = 404
            return response
        
        response = JsonResponse({"results":"found"})
        response.status_code = 200
        return response
    elif request.method == "PUT":
        # validate author id in citrus_author model:
        try:
            author = CitrusAuthor.objects.get(id=author_id)
        except ObjectDoesNotExist: 
            response = JsonResponse({"results":"author_id doesnt exist on server"})                
            response.status_code = 404
            return response

        # check if foreign author id is in citrus_author model, team 3 server or team 18 server:
        check_ours = check_author_exist_in_CitrusAuthor(foreign_author_id)
        check18 = check_author_exist_team18(foreign_author_id)
        check3 = check_author_exist_team3(foreign_author_id)

        # if none on any server, return error
        if check_author_exist_in_CitrusAuthor(foreign_author_id) == False and check18.status_code == 404 and check3.status_code == 404:
            response = JsonResponse({"results":"foreign id doesn't exist on any server"})
            response.status_code = 404
            return response
        elif check_ours == True: # if on our server, return error, follower api will do this
            response = JsonResponse({"results":"foreign id is on our server, become friend using follow api"})
            response.status_code = 405
            return response
        elif check18.status_code == 200 or check3.status_code ==200: # if on other servers, add them in friend list
            # foreign_author_id also follow author_id
            # add both of them as friend of each other in Friend model
            # check author_id exist in friend model:
            # check if they are in node model:
            if check18.status_code == 200 and not check_team18_in_node():
                response = JsonResponse({"results":"Not a Sharing Node. Please contact admin server to be added as a sharing node"})
                response.status_code = 405
                return response
            elif check3.status_code == 200 and not check_team3_in_node():
                response = JsonResponse({"results":"Not a Sharing Node. Please contact admin server to be added as a sharing node"})
                response.status_code = 405
                return response
            try:
                author_id_friends = Friend.objects.get(uuid=author)
            except ObjectDoesNotExist: # author id is not in friend model
                # create instance of the follower with uuid to author_id
                friend = str(foreign_author_id)
                new_friend_object = Friend(uuid = author,friends_uuid= friend)
                new_friend_object.save()
            else:
                # add foreign id 
                friends = str(author_id_friends.friends_uuid)+CONST_SEPARATOR+str(foreign_author_id)
                author_id_friends.friends_uuid = friends
                author_id_friends.save()

            # not checking foreign author id because they're not on our database        

            response = JsonResponse({"results":"success, added as friends"})
            response.status_code = 200
            return response
    else:
        response = JsonResponse({"message":"Method not Allowed"})
        response.status_code = 405
        return response
'''
function to render the friends page
PARAMS: request
RETURN: request, friends page, current user id
'''
def render_friends_page(request):
    uuid = get_uuid(request)
    return render(request, 'citrus_home/friends.html', {'uuid':uuid})

'''
function to render the friends page
PARAMS: request
RETURN: request, findfriends page, current user id
'''
def render_find_friends_page(request):
    uuid = get_uuid(request)
    return render(request, 'citrus_home/findfriends.html', {'uuid':uuid})

    
'''
Follow someone from team 18 === send a friend request to someone from team 18's inbox
https://app.swaggerhub.com/apis-docs/lida9/SocialDistribution/1.0.0-oas3#/Inbox/post_service_author__authorID__inbox_friendrequest__foreignAuthorID__

PARAMS:
    request - the request to endpoint 
    author_id - the id of the author the request is being sent to
    foreign_author_id - the id of the author on our server sending the request
    team_18_host - team 18s host name
'''
def be_follow_team_18(request, author_id, foreign_author_id, team_18_host):
    #pending_friends_18 = get_pending_friend_reqs(foreign_author_id,team_18_host)
    if basicAuthHandler(request):
        if request.method == 'GET':
            try:
                url = team_18_host + "service/author/" + str(author_id) + "/inbox/"
                print(url)
                body = { "type": "follow", "new_follower_ID": foreign_author_id} 
                response = requests.post(url, data = body, auth=HTTPBasicAuth(get_team_18_user(), get_team_18_password()))
                
                result = response.json()
            
                response = JsonResponse({"message from team 18's response":result})
                response.status_code = 200
                return response
            except:
                response = JsonResponse({"message":"check API endpoint?"})
                response.status_code = 404
                return response
    else:
        response = JsonResponse({"message": "Authorization required"})
        response.status_code = 401
        return response


def be_follow_back_team_18(request, author_id, foreign_author_id, team_18_host):
    if basicAuthHandler(request):
        if request.method == "GET":
            url = team_18_host + "service/author/" + str(author_id) + "/followers/" + str(foreign_author_id) + "/"
            response = requests.put(url, auth=HTTPBasicAuth(get_team_18_user(), get_team_18_password()))
            result = response.json()
            response = JsonResponse({"message from team 18's response when following back":result})
            response.status_code = 200
            return response
    else:
        response = JsonResponse({"message": "Authorization required"})
        response.status_code = 401
        return response


def be_follow_back_team_3(request, author_id, foreign_author_id, team_18_host):
    if basicAuthHandler(request):
        if request.method == "GET":
                response = JsonResponse({"message": "Cant FE team 3 yet."})
                response.status_code = 451
                return response
    else:
        response = JsonResponse({"message": "Authorization required"})
        response.status_code = 401
        return response

   
'''
determine if someones friend request is pending when we follow - if so - post into our friend api
PARAMS:
    foreign_author_id - the id of the author on our server sending the request
    team_18_host - team 18s host name
'''
def get_pending_friend_reqs_team18(author_id,team_18_host):
    pass

'''
Follow someone from team 3 === send a friend request to team 3
https://github.com/CMPUT404W21-Team3/social-distribution/wiki/API-Reference#follower-detail-view

PARAMS:
    request - the request to endpoint 
    author_id - the id of the author the request is being sent to
    foreign_author_id - the id of the author on our server sending the request
    team_3_host - team 3s host name
'''
def be_follow_team_3(request, author_id, foreign_author_id, team_3_host):
    if request.method == 'GET':
        response = JsonResponse({"message":"cant friend request or following remote auths on team 3 yet"})
        response.status_code = 404
        return response
        '''
        #https://team3-socialdistribution.herokuapp.com/api/author/7688943f-7102-4d27-ab90-4935fa5d4ee7/friendrequests/a23b6b75-c3e9-4012-b036-0f3b21af36b6
        #http://127.0.0.1:8000/service/author/7688943f-7102-4d27-ab90-4935fa5d4ee7/follow_remote_3/cf9924f7-3604-4d76-8d0f-3196aca280f1/https://team3-socialdistribution.herokuapp.com/
        print(team_3_host)
        url = team_3_host + "api/author/" + "7688943f-7102-4d27-ab90-4935fa5d4ee7" + "/friendrequests/" + "a23b6b75-c3e9-4012-b036-0f3b21af36b6"
        print("**************************")
        print(url)
        example_body = {
            "type": "Follow",
            "summary": str(foreign_author_id) + "wants to follow steve" + str(author_id),
            "sender": {
                "type": "author",
                "id": "a23b6b75-c3e9-4012-b036-0f3b21af36b6",
                "displayName": "leah_18",
                "bio": "",
                "location": "",
                "birth_date": "",
                "github": ""
            },
            "receiver": {
                "type": "author",
                "id": "7688943f-7102-4d27-ab90-4935fa5d4ee7",
                "displayName": "leah_team_3",
                "bio": "",
                "location": "",
                "birth_date": "",
                "github": ""
            }
        }

        response = requests.put(url, data = example_body)
        print(response.content)
        #result = response.json(response)
        #print(result)
       
        response_2 = JsonResponse({"message from team 3's response": "is this better"})
        return response_2
    else:
        response = JsonResponse({"message":"that wasnt a GET request bruv"})
        response.status_code = 405
        return response
    '''

"""
    render makepost html page
    create a new post using POST method for PostForm (custom django form for posts)
"""
@login_required(login_url='login_url')
def make_post_redirect(request):
    if request.method == 'GET':
        # get uuid from logged in user
        user_uuid = get_uuid(request)
        form = PostForm()
        return render(request, 'citrus_home/makepost.html', {'uuid':user_uuid, 'form': form})
    elif request.method  == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            user_uuid = get_uuid(request)
            post_id = str(uuid.uuid4())
            author = CitrusAuthor.objects.get(id=user_uuid)
            title = str(request.POST['title'])
            description = str(request.POST['description'])
            content = str(request.POST['content'])
            contentType = str(request.POST['contentType'])
            categories = str(request.POST['categories'])
            visibility = str(request.POST['visibility'])
            shared_with = str(request.POST['shared_with'])
            post = Post.objects.create(id=post_id, 
                                    title=title, 
                                    description=description, 
                                    content=content, 
                                    contentType=contentType, 
                                    categories=categories, 
                                    author=author, 
                                    origin=str(request.headers['Origin']), 
                                    source=str(request.headers['Origin']), 
                                    visibility=visibility, 
                                    shared_with=shared_with)
            return redirect(home_redirect)
        else:
            data = form.errors.as_json()
            return JsonResponse(data, status=400) 
    else:
        response = JsonResponse({
            "message": "Method Not Allowed. Only support GET."
        })
        response.status_code = 405
        return response

def get_author_post(request, author_id, post_id):
    if request.method == 'GET':
        try:
            author = CitrusAuthor.objects.get(id=author_id)
            post = Post.objects.get(id=post_id)
            author_data = convertAuthorObj(author)
            categories = post.categories.split()
            comments = Comment.objects.filter(post=post)
            comments_arr = create_comment_list(post)
            return_data = {
                    "type": "post",
                    "title": post.title,
                    "id": post.id,
                    "source": post.source,
                    "origin": post.origin,
                    "description": post.description,
                    "contentType": post.contentType,
                    "content": post.content,
                    # probably serialize author here and call it
                    "author": author_data,
                    "categories": categories,
                    "count": comments.count(),
                    "comments": comments_arr, 
                    "published": post.published,
                    "visibility": post.visibility,
                    "unlisted": "false"
                }
            return JsonResponse(return_data, status=200)
        except ObjectDoesNotExist:
            nodes = Node.objects.all()
            for node in nodes:
                if node.host == 'https://cmput-404-socialdistribution.herokuapp.com/':
                    req = requests.get(node.host + 'service/author/' + str(author_id) + '/', auth=(node.node_username, node.node_password))
                    if req.status_code == 200:
                        req = requests.get(node.host + 'service/author/' + str(author_id) + '/posts/' + post_id + '/', auth=(node.node_username, node.node_password)).json()
                        req["id"] = req["postID"]
                        req["author"]["id"] = req["authorID"]
                        return JsonResponse(req)
                elif node.host == 'https://team3-socialdistribution.herokuapp.com/':
                    req = requests.get(node.host + 'author/' + str(author_id) + '/', auth=(node.node_username, node.node_password))
                    if req.status_code == 200:
                        req = requests.get(node.host + 'author/' + str(author_id) + '/posts/' + post_id, auth=(node.node_username, node.node_password))
                        return JsonResponse(req.json())

@csrf_exempt
def handle_remote_comment(request, author_id, post_id):
    if not basicAuthHandler(request):
        response = JsonResponse({'message':'not authenticated'})
        response.status_code = 401
        return response
    try:
        current_author = CitrusAuthor.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return returnJsonResponse("not authorized", 401)
    if request.method == 'GET':
        try:
            author = CitrusAuthor.objects.get(id=author_id)
            post = Post.objects.get(id=post_id)
            comment_arr = create_comment_list(post)
            return JsonResponse({
                "comments": comment_arr
            }, status=200)
        except ObjectDoesNotExist:
            nodes = Node.objects.all()
            for node in nodes:
                if node.host == 'https://cmput-404-socialdistribution.herokuapp.com/':
                    req = requests.get(node.host + 'service/author/' + str(author_id) + '/', auth=(node.node_username, node.node_password))
                    if req.status_code == 200:
                        req = requests.get(node.host + 'service/author/' + str(author_id) + '/posts/' + str(post_id) + '/comments/', auth=(node.node_username, node.node_password))
                        return JsonResponse(req.json())
                elif node.host == 'https://team3-socialdistribution.herokuapp.com/':
                    req = requests.get(node.host + 'author/' + str(author_id) + '/', auth=(node.node_username, node.node_password))
                    if req.status_code == 200:
                        req = requests.get(node.host + 'author/' + str(author_id) + '/posts/' + str(post_id) + '/comments', auth=(node.node_username, node.node_password))
                        return JsonResponse({"comments": req.json()})

    elif request.method == 'POST':
        try:
            body = json.loads(request.body)
        except:
            return returnJsonResponse("Please provide a post body", 400)
        try:
            author = CitrusAuthor.objects.get(id=author_id)
            post = Post.objects.get(id=post_id)
            Comment.objects.create(author=author, post=post, comment=body['comment'], id=uuid.uuid4()).save()
            return returnJsonResponse(specific_message="comment added", status_code=200)
        except ObjectDoesNotExist:
            nodes = Node.objects.all()
            for node in nodes:
                if node.host == 'https://cmput-404-socialdistribution.herokuapp.com/':
                    req = requests.get(node.host + 'service/author/' + str(author_id) + '/', auth=(node.node_username, node.node_password))
                    if req.status_code == 200:
                        body["author_write_comment_ID"] = str(current_author.id)
                        req = requests.post(node.host + 'service/author/' + str(author_id) + '/posts/' + str(post_id) + '/comments/', json=body, auth=(node.node_username, node.node_password))
                        return JsonResponse(req.json())
                elif node.host == 'https://team3-socialdistribution.herokuapp.com/':
                    req = requests.get(node.host + 'author/' + str(author_id) + '/', auth=(node.node_username, node.node_password))
                    if req.status_code == 200:
                        req = requests.post(node.host + 'author/' + str(author_id) + '/posts/' + str(post_id) + '/comments', json=body, auth=(node.node_username, node.node_password))
                        return JsonResponse({"comments": req.json()})


"""
    render view post html page
    update existing form using POST method for PostForm (custom django form for posts).
"""
@login_required(login_url='login_url')
def post_redirect(request, author_id, post_id): 
    if request.method == 'GET':
        # get uuid from logged in user
        uuid = get_uuid(request)

        current_user = request.user
        current_citrus_author = CitrusAuthor.objects.get(user=current_user)
        # id of the person who owns the post
        try:
            posts = Post.objects.get(id=post_id)
            post_author = posts.author
            if current_citrus_author == post_author:
                # check if form is valid here
                post = Post.objects.get(id=post_id) 
                form = PostForm(instance=post)
                return render(request, 'citrus_home/viewpost.html', {'uuid': uuid, 'post_id': post_id, 'author_id': author_id, 'form': form})
            else:
                return render(request, 'citrus_home/viewpost.html', {'uuid': uuid, 'post_id': post_id, 'author_id': author_id})
        except ObjectDoesNotExist:
            return render(request, 'citrus_home/viewpost.html', {'uuid': uuid, 'post_id': post_id, 'author_id': author_id})

            
    elif request.method  == "POST":
        uuid = get_uuid(request)
        form = PostForm(request.POST)
        if form.is_valid():
            current_user = request.user
            current_citrus_author = CitrusAuthor.objects.get(user=current_user)
            # id of the person who owns the post
            posts = Post.objects.get(id=post_id)
            post_author = posts.author
            if current_citrus_author == post_author:
            # check if form is valid here
                post = Post.objects.get(id=post_id) 
                # update fields of the post object
                post.title = str(request.POST['title'])
                post.description = str(request.POST['description'])
                post.content = str(request.POST['content'])
                post.contentType = str(request.POST['contentType'])
                post.categories = str(request.POST['categories'])
                post.visibility = str(request.POST['visibility'])
                post.shared_with = str(request.POST['shared_with'])
                post.save()

                response = JsonResponse({
                    "message": "post updated!"
                })
                response.status_code = 200
                return render(request, 'citrus_home/viewpost.html', {'uuid': uuid, 'post_id': post_id, 'author_id': author_id, 'form': form, 'response':response,})
            else:
                return returnJsonResponse(specific_message="user doesn't have correct permissions", status_code=403)
        else:
            data = form.errors.as_json()
            return JsonResponse(data, status=400) 
    else:
        response = JsonResponse({
            "message": "Method Not Allowed. Only support GET."
        })
        response.status_code = 405
        return response

"""
handle the creation of a new post object
GET Requests:
URL: ://service/author/{AUTHOR_ID}/posts/{POST_ID} will get you the post of that author with up to 5 comments
POST Requests:
URL: ://service/author/{AUTHOR_ID}/posts/{POST_ID=null} will create the post for that author.
POST Body: {
    "title": "second post",
    "description": "description of the second post -> caruso is the goat",
    "categories": "fitness, travel, compsci",
    "content": "long detailed content of the post",
    "origin": "local host:9900"
} 
PUT Requests:
URL: ://service/author/{AUTHOR_ID}/posts/{POST_ID}
PUT Body: {
    {
    "title": "goat post",
    "description": "Caruso is the goat",
    "categories": "fitness, travel, compscience",
    "content": "first post with new API",
    "origin": "local host:9900",
    "private_to_author": "True",
    "public": "False",
    "private_to_friend": "False",
    "shared_with": "alex"
}
}
DELETE Requests:
URL: ://service/author/{AUTHOR_ID}/posts/{POST_ID} -> this will delete the post with the id you provided. 
"""
# the csrf_exempt token is there if you're testing with postman
@csrf_exempt
def manage_post(request, id, **kwargs):
    if not basicAuthHandler(request):
        response = JsonResponse({'message':'not authenticated'})
        response.status_code = 401
        return response
    pid = kwargs.get('pid')
    print(request.method)
    if request.method == "POST":
        #
        body = json.loads(request.body)
        author = CitrusAuthor.objects.get(id=id)
        post = Post.objects.create(id=str(uuid.uuid4()), 
                                title=body['title'], 
                                description=body['description'],
                                content=body['content'],
                                contentType=body['contentType'],
                                categories=body['categories'],
                                author=author,
                                origin=body['origin'],
                                source=body['origin'],
                                visibility=body['visibility'],
                                shared_with=body['shared_with'])
        return returnJsonResponse(specific_message="post created", status_code=201)

    
    elif request.method == 'DELETE':
        # get current user
        current_user = request.user
        current_citrus_author = CitrusAuthor.objects.get(user=current_user)
        # id of the person who owns the post
        posts = Post.objects.get(id=pid)
        post_author = posts.author
        if current_citrus_author == post_author:
            posts_current = Post.objects.get(id=pid)
            posts_current.delete()
            return returnJsonResponse(specific_message="post deleted", status_code=200)

    # update an existing post made by the user
    elif request.method == "PUT":
        # verify that the owner of the post is trying to change the post
        # author = CitrusAuthor.objects.get(id=id)
        # posts = Post.objects.get(id=pid)
        # post_author = posts.author
        # if author == post_author:
        # get current user
        current_user = request.user
        current_citrus_author = CitrusAuthor.objects.get(user=current_user)
        # id of the person who owns the post
        posts = Post.objects.get(id=pid)
        post_author = posts.author
        if current_citrus_author == post_author:
        # check if form is valid here
            body = json.loads(request.body)
            author = CitrusAuthor.objects.get(id=id)
            post = Post.objects.get(id=pid) 
            # update fields of the post object
            post.title = body['title']
            post.description = body['description']
            post.content = body['content']
            post.contentType = body['contentType']
            post.visibility = body['visibility']
            post.shared_with = body['shared_with']
            post.save()
            return returnJsonResponse(specific_message="post updated", status_code=200)
        else:
            return returnJsonResponse(specific_message="user doesn't have correct permissions", status_code=403)

    elif request.method == "GET":
        # print(request.META['host'])
        # ^^ HOW TO GET REQUEST HEADERS ^^
        # return 1 post
        if pid:
            author = CitrusAuthor.objects.get(id=id)
            posts = Post.objects.get(id=pid)
            comments = Comment.objects.filter(post=posts)
            comments_arr = create_comment_list(posts)
            author_data = convertAuthorObj(author)
            # check for post categories and put them into an array
            categories = posts.categories.split()
            return_data = {
                "type": "post",
                "title": posts.title,
                "id": posts.id,
                "source": "localhost:8000/some_random_source",
                "origin": posts.origin,
                "description": posts.description,
                "contentType": posts.contentType,
                "content": posts.content,
                # probably serialize author here and call it
                "author": author_data,
                "categories": categories,
                "count": comments.count(),
                "comments": comments_arr, 
                "published": posts.published,
                "visibility": posts.visibility,
                "unlisted": "false"
            }
            return JsonResponse(return_data, status=200)
        # return all posts of the author ordered by most recent posts
        else:
            # return all posts of the given user
            author = CitrusAuthor.objects.get(id=id)
            visibility_list = ['PUBLIC']
            posts = Post.objects.filter(author=author,visibility__in=visibility_list).order_by('-published')
            json_posts = []
            for post in posts:
                author = post.author
                comments = Comment.objects.filter(post=post)
                comments_arr = create_comment_list(post)
                author_data = convertAuthorObj(author)
                categories = post.categories.split()
                return_data = {
                    "type": "post",
                    "title": post.title,
                    "id": post.id,
                    "source": "localhost:8000/some_random_source",
                    "origin": post.origin,
                    "description": post.description,
                    "contentType": post.contentType,
                    "content": post.content,
                    # probably serialize author here and call it
                    "author": author_data,
                    "categories": categories,
                    "count": comments.count(),
                    "comments": comments_arr, 
                    "published": post.published,
                    "visibility": post.visibility,
                    "unlisted": "false"
                }
                json_posts.append(return_data)

            return JsonResponse({
                "posts": json_posts
            },status=200)
    else:
        return returnJsonResponse(specific_message="method not supported", status_code=400)

"""
handles GET & POST requests for comments
"""
@csrf_exempt
def handle_comment(request, id, pid):
    if not basicAuthHandler(request):
        response = JsonResponse({'message':'not authenticated'})
        response.status_code = 401
        return response
    if request.method == "POST":
        print("inside handle comments")
        # create a comment and attach it to the post matching the provided post id
        body, post, author = setup(request, id, pid)
        Comment.objects.create(author=author, post=post, comment=body['comment'], id=uuid.uuid4()).save()
        return returnJsonResponse(specific_message="comment added", status_code=200)
    
    elif request.method == "GET":
        # check the request to see if there's a specified indices of comments requested. 
        post = Post.objects.get(id=pid)
        comment_arr = create_comment_list(post)
        return JsonResponse({
            "comments": comment_arr
        }, status=200)

    else:
        return returnJsonResponse(specific_message="method not available", status_code=400)


"""
arguments: takes in a post object and optionally a start and end index
return: a list of comments for the specified post
"""
def create_comment_list(post, **kwargs):
    # if start index and end index arguemnts provided return specified indices
    if "start_index" and "end_index" in kwargs:
        start_index = kwargs.get('start_index')
        end_index = kwargs.get('end_index')
        # get all comments associated with this post and sort by most recently published
        comments = Comment.objects.filter(post=post).order_by('-published')[start_index:end_index+1]
    else:
        comments = Comment.objects.filter(post=post).order_by('-published')[:5]
    comments_arr = []
    for comment in comments:
            # get the author of the comment
        author = CitrusAuthor.objects.get(id=comment.author.id)
        comment_data = {
            "type": "comment", 
            "author": convertAuthorObj(author),
            "comment": comment.comment,
            "contentType": "text/markdown",
            "published": comment.published,
            "id": comment.id,
        }
        comments_arr.append(comment_data)
    return comments_arr


"""
arguments: request, author id, post id
returns: returns the body of the request, the CitrusAuthor object associated with the id and the Post object associated with the pid
"""
def setup(request, id, pid):
        return json.loads(request.body), Post.objects.get(id=pid), CitrusAuthor.objects.get(id=id)


"""
arguments: message, status_code
return: custom json response
"""
def returnJsonResponse(specific_message, status_code):
    return JsonResponse({
        "message": specific_message
    }, status=status_code)


"""
arguments: CitrusAuthor object
return: dictionary with CitrusAuthor fields
"""
def convertAuthorObj(author):
        author_data = {
            "type": author.type,
            "id": author.id,
            "host": author.host,
            "displayName": author.displayName,
            "url": "somerandomUrl for now",
            "github": author.github
        }
        return author_data


"""
arguments: string that reads true or false
return: boolean value of string
"""
def stringToBool(value):
    if value == "True": 
        return True
    elif value == "False":
        return False


"""
If a user is signed in a GET request to localhost:8000/home-test/ will return a list of posts of all
friends of the signed in user (most recent posts first that are all public)
"""
def handleStream(request):
    if not basicAuthHandler(request):
        response = JsonResponse({'message':'not authenticated'})
        response.status_code = 401
        return response
    # get current user and find corresponding citrus author
    if request.method == "GET":
        current_user = request.user
        citrus_author = CitrusAuthor.objects.get(user=current_user)
        # find friends of the citrus author and get their posts
        json_posts = []
        try:
            friends = Friend.objects.get(uuid=citrus_author)
            # friends arr holds the uuid for each friend of the current user that is signed in
            friends_uuid_arr = friends.friends_uuid.split(CONST_SEPARATOR)
            friends_arr = []
            # get all active nodes and check for team 3 and 18
            # sort friends by server
            server_list = []
            try:
                nodes = Node.objects.all()
                # list of all hostnames 
                for server in nodes:
                    server_list.append(server.host)
            except:
                pass
            team18_url = "https://cmput-404-socialdistribution.herokuapp.com"
            team3_url = "https://team3-socialdistribution.herokuapp.com/"
            team18_friends = []
            team3_friendss = []
            try:      
                team18_friends = get_team18_friends(friends_uuid_arr, team18_url)
                team3_friends = get_team3_friends(friends_uuid_arr, team3_url)
                friends_uuid_arr = set(friends_uuid_arr).difference(team18_friends)
                friends_uuid_arr = set(friends_uuid_arr).difference(team3_friends)
            except:
                pass
            # citrus network database
            for id in friends_uuid_arr:
                # team 9 stores id's with a hyphen
                author = CitrusAuthor.objects.get(id=id)
                friends_arr.append(author)
            
            # query team18 database
            if team18_friends:
                for id in team18_friends:
                    request = f"{team18_url}/service/author/{id}/posts/"
                    # print(request)
                    response = requests.get(request)
                    # decode the response
                    content = json.loads(response.content)
                    post_list = content.get('posts')
                    for post in post_list:
                        # check to see if post is private to friends?
                        if post.get('visibility') == 'PUBLIC' or 'FRIEND':
                            json_posts.append(post)
            for id in friends_uuid_arr:
                author = CitrusAuthor.objects.get(id=id)
                friends_arr.append(author)

            # now you have a list of authors that are friends of the signed in user find the posts and return them
            # append current user's posts also (user story i want to post to my stream)
            friends_arr.append(citrus_author)
            posts_arr = []
            visibility_list=['PUBLIC', 'PRIVATE_TO_FRIENDS']
            # for now we are only looking for public posts this will later be extended to private to author and private to friends
            posts = Post.objects.filter(author__in=friends_arr,visibility__in=visibility_list).order_by('-published')
            for post in posts:
                author = post.author
                comments = Comment.objects.filter(post=post)
                comments_arr = create_comment_list(post)
                author_data = convertAuthorObj(author)
                categories = post.categories.split()
                return_data = {
                    "type": "post",
                    "title": post.title,
                    "id": post.id,
                    "source": post.source,
                    "origin": post.origin,
                    "description": post.description,
                    "contentType": post.contentType,
                    "content": post.content,
                    # probably serialize author here and call it
                    "author": author_data,
                    "categories": categories,
                    "count": comments.count(),
                    "comments": comments_arr, 
                    "published": post.published,
                    "visibility": post.visibility,
                    "unlisted": post.unlisted
                }
                json_posts.append(return_data)
            
            return JsonResponse({
                "posts": json_posts
            },status=200)
        except ObjectDoesNotExist:
            try:
                no_friends = Post.objects.filter(author=citrus_author)
                friends_arr = []
                friends_arr.append(citrus_author)
                posts_arr = []
                # for now we are only looking for public posts this will later be extended to private to author and private to friends
                visibility_list=['PUBLIC']
                posts = Post.objects.filter(author__in=friends_arr,visibility__in=visibility_list).order_by('-published')
                json_posts = []
                for post in posts:
                    author = post.author
                    comments = Comment.objects.filter(post=post)
                    comments_arr = create_comment_list(post)
                    author_data = convertAuthorObj(author)
                    categories = post.categories.split()
                    return_data = {
                        "type": "post",
                        "title": post.title,
                        "id": post.id,
                        "source": "localhost:8000/some_random_source",
                        "origin": post.origin,
                        "description": post.description,
                        "contentType": post.contentType,
                        "content": post.content,
                        # probably serialize author here and call it
                        "author": author_data,
                        "categories": categories,
                        "count": comments.count(),
                        "comments": comments_arr, 
                        "published": post.published,
                        "visibility": post.visibility,
                        "unlisted": "false"
                    }
                    json_posts.append(return_data)
                
                return JsonResponse({
                    "posts": json_posts
                },status=200)
                
            except ObjectDoesNotExist:
                return returnJsonResponse(specific_message="make some friends :)", status_code=401)
    
    else:
        return returnJsonResponse(specific_message="method not available", status_code=400)
    
@csrf_exempt
def handle_inbox(request, author_id):
    if not basicAuthHandler(request):
        response = JsonResponse({'message':'not authenticated'})
        response.status_code = 401
        return response
    if request.method == "GET":
        try:
            author = CitrusAuthor.objects.get(id=author_id)
        except ObjectDoesNotExist:
            return returnJsonResponse(specific_message="author not found", status_code=400)

        try:
            current_user = request.user
            current_citrus_author = CitrusAuthor.objects.get(user=current_user) 
        except:
            return returnJsonResponse(specific_message="user doesn't have correct permissions", status_code=401)

        if str(current_citrus_author.id) != str(author_id):
            return returnJsonResponse(specific_message="user doesn't have correct permissions", status_code=401)
        return_data = {
            "type":"inbox",
            "author":author_id
        }
        try:
            inbox = Inbox.objects.get(author=author)
            return_data["items"] = json.loads(inbox.items)
        except ObjectDoesNotExist:
            return_data["items"] = []
        return JsonResponse(return_data, status=200)

    elif request.method == "POST":
        body = json.loads(request.body)
        try:
            author = CitrusAuthor.objects.get(id=author_id)
        except ObjectDoesNotExist:
            return returnJsonResponse(specific_message="author not found", status_code=400)
        try:
            if ("post" not in body["type"].lower() and "like" not in body["type"].lower() and \
                "follow" not in body["type"].lower()):
                return returnJsonResponse(specific_message="invalid type", status_code=400)
            # handle friend request from other servers
            elif ("follow" in body["type"].lower()):
                # get the id of the follower
                actor_id = body["actor"]["id"]
                # check the format of the id: either url format or just uuid
                if ("author" in actor_id):
                    actor_id = body["actor"]["authorID"]
                # check author_id in our model
                if check_author_exist_in_CitrusAuthor(author_id) == False:
                    response = JsonResponse({"results":"Author Id doesn't exist"})
                    response.status_code = 404
                    return response
                # check if is actor_id is in our sharing node:
                elif check_author_exist_team3(actor_id).status_code == 200 and (not check_team3_in_node()):
                    response = JsonResponse({"results":"actor id is not in any existing sharing node. Contact admin server to add your node to our server"})
                    response.status_code = 405
                    return response
                elif check_author_exist_team18(actor_id).status_code == 200 and (not check_team18_in_node()):
                    response = JsonResponse({"results":"actor id is not in any existing sharing node. Contact admin server to add your node to our server"})
                    response.status_code = 405
                    return response                    
                # add the actor_id to the author_id list of followers
                if check_author_exist_in_Follower(author_id): # add actor_id into the list of followers
                    # get Citrus Author object with author id
                    author = CitrusAuthor.objects.get(id=author_id)
                    # get follower object with citrus author object
                    result = Follower.objects.get(uuid=author)
                    # check if foreign id is already a follower
                    followers = str(result.followers_uuid)
                    if str(actor_id) in followers:
                        response = JsonResponse({"results":"actor id is already a follower"})
                        response.status_code = 304
                        return response

                    # check if author_id also follows actor_id then befriend
                    # check if author_id is a follower by calling their api:
                    check_team3 = check_author_exist_team3(actor_id)
                    check_team18 = check_author_exist_team18(actor_id)
                    # if the actor id doesnt exist for both server
                    if check_team3.status_code == 404 and check_team18.status_code == 404:
                        response = JsonResponse({"results":"actor id doesn't exist in remote server"})
                        response.status_code = 404
                        return response
                    # if the actor id exists on team 3 server
                    elif check_team3.status_code==200:
                        # check if author_id already follows actor id:
                        check_follow_team3 = check_author_follows_actor_team3(author_id,actor_id)
                        if check_follow_team3.status_code == 200:
                            # if yes, condition satisfied (both are following each other), befriend
                            # check if author_id already in Friend model
                            # existed so add actor_id in
                            if check_author_exist_in_Friend(author_id):
                                # get author object by author id
                                author = CitrusAuthor.objects.get(id=author_id)
                                # get friend object by author object
                                author_id_friends = Friend.objects.get(uuid=author)
                                # add foreign id 
                                friends = str(author_id_friends.friends_uuid)+CONST_SEPARATOR+str(actor_id)
                                author_id_friends.friends_uuid = friends
                                author_id_friends.save()
                            else: # not existed, create new one and add actor_id as a friend
                                # create instance of the follower with uuid to author_id
                                friend = str(actor_id)
                                author = CitrusAuthor.objects.get(id=author_id)

                                new_friend_object = Friend(uuid = author,friends_uuid= friend)
                                new_friend_object.save()
                    # if the actor id exists on team 18 server
                    elif check_team18.status_code==200:
                        # check if author_id already follows actor id:
                        check_follow_team18 = check_author_follows_actor_team18(author_id,actor_id).json()
                        # if yes, condition satisfied (both are following each other), befriend
                        if  check_follow_team18['message'] == True:
                            # if yes, condition satisfied (both are following each other), befriend
                            # check if author_id already in Friend model
                            # existed so add actor_id in
                            if check_author_exist_in_Friend(author_id):
                                # get author object by author id
                                author = CitrusAuthor.objects.get(id=author_id)
                                # get friend object by author object
                                author_id_friends = Friend.objects.get(uuid=author)
                                # add foreign id 
                                friends = str(author_id_friends.friends_uuid)+CONST_SEPARATOR+str(actor_id)
                                author_id_friends.friends_uuid = friends
                                author_id_friends.save()
                            else: # not existed, create new one and add actor_id as a friend
                                # create instance of the follower with uuid to author_id
                                friend = str(actor_id)
                                author = CitrusAuthor.objects.get(id=author_id)

                                new_friend_object = Friend(uuid = author,friends_uuid= friend)
                                new_friend_object.save()

                    # add actor id 
                    followers = str(result.followers_uuid)+CONST_SEPARATOR+str(actor_id)
                    result.followers_uuid = followers
                    result.save()                    

                else: # this author_id has no follower so needs to creat new instance 
                    followers = str(actor_id)
                    # get Citrus Author object with author id
                    author = CitrusAuthor.objects.get(id=author_id)
                    # create instance of the follower with uuid to author_id
                    new_follower_object = Follower(uuid = author,followers_uuid= followers)
                    new_follower_object.save()

                     
            inbox = Inbox.objects.get(author=author)
            items = json.loads(inbox.items)
            items.insert(0, body)
            inbox.items = json.dumps(items)
            inbox.save()
        except ObjectDoesNotExist:
            inbox = Inbox.objects.create(author=author, items='[' + json.dumps(body) + ']')
            return returnJsonResponse(specific_message="success", status_code=201)

        return JsonResponse(body, status=201)

    elif request.method == "DELETE":
        try:
            current_user = request.user
            current_citrus_author = CitrusAuthor.objects.get(user=current_user) 
        except:
            return returnJsonResponse(specific_message="user doesn't have correct permissions", status_code=401)

        if str(current_citrus_author.id) != str(author_id):
            return returnJsonResponse(specific_message="user doesn't have correct permissions", status_code=401)
        try:
            author = CitrusAuthor.objects.get(id=author_id)
        except ObjectDoesNotExist:
            return returnJsonResponse(specific_message="author not found", status_code=400)
        try:
            inbox = Inbox.objects.get(author=author)
            inbox.delete()
            return returnJsonResponse(specific_message="inbox deleted", status_code=200)
        except ObjectDoesNotExist:
            return returnJsonResponse(specific_message="inbox deleted", status_code=200)
    else:
        return returnJsonResponse(specific_message="method not available", status_code=405)

@login_required(login_url='login_url')
def inbox_redirect(request):
    if request.method == "GET":
        uuid = get_uuid(request)
        return render(request, 'citrus_home/inbox.html', {'uuid':uuid})


"""
function to return all public posts (local for now)
search parameters can be provided:
localhost:8000/public-posts?q=searchparamter searchparamter2 searchparameterk
localhost:800/public-posts?q=arg1%20arg2
"""
@csrf_exempt
def browse_posts(request):
    if not basicAuthHandler(request):
        response = JsonResponse({'message':'not authenticated'})
        response.status_code = 401
        return response
    # return all public posts
    if request.method == "GET":
        try:
            search_paramaters = request.GET.get('q').split()
            # Post: https://stackoverflow.com/a/4824810 Author: https://stackoverflow.com/users/20862/ignacio-vazquez-abrams referenced: 24/03/2021
            public_posts = Post.objects.filter(visibility='PUBLIC').filter(reduce(operator.or_, (Q(title__contains=x)for x in search_paramaters))).order_by("-published")
        except:
            print("here")
            public_posts = Post.objects.filter(visibility='PUBLIC').order_by('-published')
        json_posts = []
        for post in public_posts:
            author = post.author
            comments = Comment.objects.filter(post=post)
            comments_arr = create_comment_list(post)
            author_data = convertAuthorObj(author)
            categories = post.categories.split()
            return_data = {
                "type": "post",
                "title": post.title,
                "id": post.id,
                "source": post.source,
                "origin": post.origin,
                "description": post.description,
                "contentType": post.contentType,
                "content": post.content,
                # probably serialize author here and call it
                "author": author_data,
                "categories": categories,
                "count": comments.count(),
                "comments": comments_arr, 
                "published": post.published,
                "visibility": post.visibility,
                "unlisted": post.unlisted
            }
            json_posts.append(return_data)
        try:
            nodes = Node.objects.all()
            # list of all hostnames 
            server_list = []
            for server in nodes:
                server_list.append(server.host)

            for hostname in server_list:
                print(hostname)
                if hostname == "https://cmput-404-socialdistribution.herokuapp.com/":
                    request = f"{hostname}service/allposts/"
                    response = requests.get(request,auth=HTTPBasicAuth(get_team_18_user(), get_team_18_password()))
                    # decode the response
                    content = json.loads(response.content)
                    post_list = content.get('posts')
                    for post in post_list:
                        json_posts.append(post)
                elif hostname == "https://team3-socialdistribution.herokuapp.com/":
                    request = f"{hostname}posts"
                    response = requests.get(request)
                    # decode the response
                    content = json.loads(response.content)
                    for post in content:
                        json_posts.append(post)
        except:
            pass
        # return JsonResponse(return_data, status=200)
        return returnJsonResponse(json_posts, status_code=200)
    
    else:
        return returnJsonResponse(specific_message="method not supported", status_code=400)

@login_required(login_url='login_url')
def public_posts_redirect(request):
    if request.method == "GET":
        return render(request, 'citrus_home/publicposts.html')

def handle_likes(request, **kwargs):
    if not basicAuthHandler(request):
        response = JsonResponse({'message':'not authenticated'})
        response.status_code = 401
        return response
    # return either likes on post or comment
    if request.method == "GET":
        # look specifically for likes on comments
        response = []
        # URL: ://service/author/{author_id}/post/{post_id}/comments/{comment_id}/likes
        # GET a list of likes from other authors on author_id’s post post_id comment comment_id
        if 'comment_id' in kwargs:
            # get comment_id since it was provided
            comment_id = kwargs.get('comment_id')
            print(comment_id)
            list_of_comments = Like.objects.filter(comment_id=comment_id)
            for comment in list_of_comments:
                # call function to create like object
                like_object = return_like_object("Like", comment, False, request)
                response.append(like_object)
            jsonResponse =  JsonResponse({
                "likes": response
            })
            jsonResponse.status_code = 200
            return jsonResponse
        # URL: ://service/author/{author_id}/post/{post_id}/likes
        # GET a list of likes from other authors on author_id’s post post_id
        elif 'post_id' in kwargs:
            # get post_id since it was provided
            post_id = kwargs.get('post_id')
            list_of_likes = Like.objects.filter(post_id=post_id)
            print(list_of_likes)
            json_like_response = []
            for like in list_of_likes:
                # call function to create like object
                like_object = return_like_object("Like",like,True, request)
                response.append(like_object)
            jsonResponse =  JsonResponse({
                "likes": response
            })
            jsonResponse.status_code = 200
            return jsonResponse
        # URL: ://service/author/{author_id}/liked
        # GET list what public things author_id liked.
        # It’s a list of of likes originating from this author
        else:
            author_id = kwargs.get('author_id')
            all_liked_objects = Like.objects.filter(author=author_id)
            for like in all_liked_objects:
                if like.comment_id:
                    like_object = return_like_object("Like",like,False, request)
                    response.append(like_object)
                else:
                    like_object = return_like_object("Like",like,True, request)
                    response.append(like_object)
            jsonResponse = JsonResponse({
                "type": "liked",
                "items": response
            })
            jsonResponse.status_code = 200
            return jsonResponse

    else:
        return returnJsonResponse(specific_message="Method Not Allowed", status_code=405)


"""
this function probably needs to take in the request to properly parse the host address
"""
def return_like_object(type, like, post, request):
    # like object is a post
    author_id = like.author
    author = CitrusAuthor.objects.get(id=author_id)
    if post:
        response = {
            "@context": request.META['HTTP_HOST'],
            "summary": author.displayName + " likes your post",
            "type": type, 
            "author": convertAuthorObj(author),
            "object": request.META['HTTP_HOST']
        }
        print(response)
        return response
    # like object is a comment
    else:
        response = {
            "@context": request.META['HTTP_HOST'],
            "summary": author.displayName + " likes your comment",
            "type": type, 
            "author": convertAuthorObj(author),
            "object": request.META['HTTP_HOST']
        }
        return response

# return intersection of all users on team 18 and friends of current user
def get_team18_friends(friends_uuid_arr, host_name):
    # get all user id's on team 18's server
    request = f"{host_name}/service/author/"
    response = requests.get(request)
    content = json.loads(response.content)
    team_18_id = []
    for author in content:
        team_18_id.append((author.get('authorID')))
    return set(friends_uuid_arr).intersection(team_18_id)

# https://team3-socialdistribution.herokuapp.com/
def get_team3_friends(friends_uuid_arr, host_name):
    # get all user id's on team 18's server
    team_3_id = []
    response = get_team3_authors()
    for author in response:
        team_3_id.append((author.get('id')))
    return set(friends_uuid_arr).intersection(team_3_id)