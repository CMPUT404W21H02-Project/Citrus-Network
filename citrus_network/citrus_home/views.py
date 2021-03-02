from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import CitrusAuthor, Friend, Follower
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

# separator of uuids in list of followers and friends
CONST_SEPARATOR = " "

# @login_required
def home_redirect(request):
    if request.method == 'GET':
        mock_response = [
            {
                "type":"inbox",
                "author":"http://127.0.0.1:5454/author/c1e3db8ccea4541a0f3d7e5c75feb3fb",
                "items":[
                    {
                        "type":"post",
                        "title":"A Friendly post title about a post about web dev",
                        "id":"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
                        "source":"http://lastplaceigotthisfrom.com/posts/yyyyy",
                        "origin":"http://whereitcamefrom.com/posts/zzzzz",
                        "description":"This post discusses stuff -- brief",
                        "contentType":"text/plain",
                        "content":"Þā wæs on burgum Bēowulf Scyldinga, lēof lēod-cyning, longe þrāge folcum gefrǣge (fæder ellor hwearf, aldor of earde), oð þæt him eft onwōc hēah Healfdene; hēold þenden lifde, gamol and gūð-rēow, glæde Scyldingas. Þǣm fēower bearn forð-gerīmed in worold wōcun, weoroda rǣswan, Heorogār and Hrōðgār and Hālga til; hȳrde ic, þat Elan cwēn Ongenþēowes wæs Heaðoscilfinges heals-gebedde. Þā wæs Hrōðgāre here-spēd gyfen, wīges weorð-mynd, þæt him his wine-māgas georne hȳrdon, oð þæt sēo geogoð gewēox, mago-driht micel. Him on mōd bearn, þæt heal-reced hātan wolde, medo-ærn micel men gewyrcean, þone yldo bearn ǣfre gefrūnon, and þǣr on innan eall gedǣlan geongum and ealdum, swylc him god sealde, būton folc-scare and feorum gumena. Þā ic wīde gefrægn weorc gebannan manigre mǣgðe geond þisne middan-geard, folc-stede frætwan. Him on fyrste gelomp ǣdre mid yldum, þæt hit wearð eal gearo, heal-ærna mǣst; scōp him Heort naman, sē þe his wordes geweald wīde hæfde. Hē bēot ne ālēh, bēagas dǣlde, sinc æt symle. Sele hlīfade hēah and horn-gēap: heaðo-wylma bād, lāðan līges; ne wæs hit lenge þā gēn þæt se ecg-hete āðum-swerian 85 æfter wæl-nīðe wæcnan scolde. Þā se ellen-gǣst earfoðlīce þrāge geþolode, sē þe in þȳstrum bād, þæt hē dōgora gehwām drēam gehȳrde hlūdne in healle; þǣr wæs hearpan swēg, swutol sang scopes. Sægde sē þe cūðe frum-sceaft fīra feorran reccan",
                        "author":{
                            "type":"author",
                            "id":"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                            "host":"http://127.0.0.1:5454/",
                            "displayName":"Lara Croft",
                            "url":"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                            "github": "http://github.com/laracroft"
                        },
                        "categories":["web","tutorial"],
                        "comments":"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
                        "published":"2015-03-09T13:07:04+00:00",
                        "visibility":"FRIENDS",
                        "unlisted":False
                    },
                    {
                        "type":"post",
                        "title":"DID YOU READ MY POST YET?",
                        "id":"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/999999983dda1e11db47671c4a3bbd9e",
                        "source":"http://lastplaceigotthisfrom.com/posts/yyyyy",
                        "origin":"http://whereitcamefrom.com/posts/aaaa",
                        "description":"Whatever",
                        "contentType":"text/plain",
                        "content":"Are you even reading my posts Arjun?",
                        "author":{
                            "type":"author",
                            "id":"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                            "host":"http://127.0.0.1:5454/",
                            "displayName":"Lara Croft",
                            "url":"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                            "github": "http://github.com/laracroft"
                        },
                        "categories":["web","tutorial"],
                        "comments":"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
                        "published":"2015-03-09T13:07:04+00:00",
                        "visibility":"FRIENDS",
                        "unlisted":False
                    }
                ]
            }
        ]
        
        return render(request, 'citrus_home/index.html', {'inbox': mock_response})

def make_post_redirect(request):
    if request.method == 'GET':
        return render(request, 'citrus_home/makepost.html')

def post_redirect(request): 
    if request.method == 'GET':
        mock_response = {
            'type':"post",
            'title':"A post title about a post about web dev",
            'id':"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
            'source':"http://lastplaceigotthisfrom.com/posts/yyyyy",
            'origin':"http://whereitcamefrom.com/posts/bbbzz",
            'description':"This post discusses stuff -- brief",
            'contentType':"text/plain",
            'content':"Þā wæs on burgum Bēowulf Scyldinga, lēof lēod-cyning, longe þrāge folcum gefrǣge (fæder ellor hwearf, aldor of earde), oð þæt him eft onwōc hēah Healfdene; hēold þenden lifde, gamol and gūð-rēow, glæde Scyldingas. Þǣm fēower bearn forð-gerīmed in worold wōcun, weoroda rǣswan, Heorogār and Hrōðgār and Hālga til; hȳrde ic, þat Elan cwēn Ongenþēowes wæs Heaðoscilfinges heals-gebedde. Þā wæs Hrōðgāre here-spēd gyfen, wīges weorð-mynd, þæt him his wine-māgas georne hȳrdon, oð þæt sēo geogoð gewēox, mago-driht micel. Him on mōd bearn, þæt heal-reced hātan wolde, medo-ærn micel men gewyrcean, þone yldo bearn ǣfre gefrūnon, and þǣr on innan eall gedǣlan geongum and ealdum, swylc him god sealde, būton folc-scare and feorum gumena. Þā ic wīde gefrægn weorc gebannan manigre mǣgðe geond þisne middan-geard, folc-stede frætwan. Him on fyrste gelomp ǣdre mid yldum, þæt hit wearð eal gearo, heal-ærna mǣst; scōp him Heort naman, sē þe his wordes geweald wīde hæfde. Hē bēot ne ālēh, bēagas dǣlde, sinc æt symle. Sele hlīfade hēah and horn-gēap: heaðo-wylma bād, lāðan līges; ne wæs hit lenge þā gēn þæt se ecg-hete āðum-swerian 85 æfter wæl-nīðe wæcnan scolde. Þā se ellen-gǣst earfoðlīce þrāge geþolode, sē þe in þȳstrum bād, þæt hē dōgora gehwām drēam gehȳrde hlūdne in healle; þǣr wæs hearpan swēg, swutol sang scopes. Sægde sē þe cūðe frum-sceaft fīra feorran reccan",
            # the author has an ID where by authors can be disambiguated
            'author':{
                'type':"author",
                'id':"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                'host':"http://127.0.0.1:5454/",
                'displayName':"Lara Croft",
                'url':"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                'github': "http://github.com/laracroft"
            },
            'categories':["web","tutorial"],
            'count': 1023,
            'size': 50,
            'comments':[
                {
                    'type':"comment",
                    'author':{
                        'type':"author",
                        # ID of the Author (UUID)
                        'id':"http://127.0.0.1:5454/author/1d698d25ff008f7538453c120f581471",
                        # url to the authors information
                        'url':"http://127.0.0.1:5454/author/1d698d25ff008f7538453c120f581471",
                        'host':"http://127.0.0.1:5454/",
                        "displayName":"Greg Johnson",
                        # HATEOS url for Github API
                        'github': "http://github.com/gjohnson"
                    },
                    'comment':"Sick Olde English",
                    'contentType':"text/markdown",
                    # ISO 8601 TIMESTAMP
                    'published':"2015-03-09T13:07:04+00:00",
                    # ID of the Comment (UUID)
                    'id':"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c",
                },
                {
                    'type':"comment",
                    'author':{
                        'type':"author",
                        # ID of the Author (UUID)
                        'id':"http://127.0.0.1:5454/author/1d698d25ff008f7538453c120f581471",
                        # url to the authors information
                        'url':"http://127.0.0.1:5454/author/1d698d25ff008f7538453c120f581471",
                        'host':"http://127.0.0.1:5454/",
                        "displayName":"Greg Johnson",
                        # HATEOS url for Github API
                        'github': "http://github.com/gjohnson"
                    },
                    'comment':"Sick Olde English",
                    'contentType':"text/markdown",
                    # ISO 8601 TIMESTAMP
                    'published':"2015-03-09T13:07:04+00:00",
                    # ID of the Comment (UUID)
                    'id':"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c",
                }, 
                {
                    'type':"comment",
                    'author':{
                        'type':"author",
                        # ID of the Author (UUID)
                        'id':"http://127.0.0.1:5454/author/1d698d25ff008f7538453c120f581471",
                        # url to the authors information
                        'url':"http://127.0.0.1:5454/author/1d698d25ff008f7538453c120f581471",
                        'host':"http://127.0.0.1:5454/",
                        "displayName":"Greg Johnson",
                        # HATEOS url for Github API
                        'github': "http://github.com/gjohnson"
                    },
                    'comment':"Sick Olde English",
                    'contentType':"text/markdown",
                    # ISO 8601 TIMESTAMP
                    'published':"2015-03-09T13:07:04+00:00",
                    # ID of the Comment (UUID)
                    'id':"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c",
                }
            ],
            'published':"2015-03-09T13:07:04+00:00",
            'visibility':"PUBLIC",
            'unlisted': False,
        }
        return render(request, 'citrus_home/viewpost.html', {'post': mock_response})

def stream_redirect(request):
    if request.method == 'GET':
        mock_response = [
            {
                'type':"post",
                'title':"A post title about a post about web dev",
                'id':"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
                'source':"http://lastplaceigotthisfrom.com/posts/yyyyy",
                'origin':"http://whereitcamefrom.com/posts/zzbbzzz",
                'description':"This post discusses stuff -- brief",
                'contentType':"text/plain",
                'content':"Þā wæs on burgum Bēowulf Scyldinga, lēof lēod-cyning, longe þrāge folcum gefrǣge (fæder ellor hwearf, aldor of earde), oð þæt him eft onwōc hēah Healfdene; hēold þenden lifde, gamol and gūð-rēow, glæde Scyldingas. Þǣm fēower bearn forð-gerīmed in worold wōcun, weoroda rǣswan, Heorogār and Hrōðgār and Hālga til; hȳrde ic, þat Elan cwēn Ongenþēowes wæs Heaðoscilfinges heals-gebedde. Þā wæs Hrōðgāre here-spēd gyfen, wīges weorð-mynd, þæt him his wine-māgas georne hȳrdon, oð þæt sēo geogoð gewēox, mago-driht micel. Him on mōd bearn, þæt heal-reced hātan wolde, medo-ærn micel men gewyrcean, þone yldo bearn ǣfre gefrūnon, and þǣr on innan eall gedǣlan geongum and ealdum, swylc him god sealde, būton folc-scare and feorum gumena. Þā ic wīde gefrægn weorc gebannan manigre mǣgðe geond þisne middan-geard, folc-stede frætwan. Him on fyrste gelomp ǣdre mid yldum, þæt hit wearð eal gearo, heal-ærna mǣst; scōp him Heort naman, sē þe his wordes geweald wīde hæfde. Hē bēot ne ālēh, bēagas dǣlde, sinc æt symle. Sele hlīfade hēah and horn-gēap: heaðo-wylma bād, lāðan līges; ne wæs hit lenge þā gēn þæt se ecg-hete āðum-swerian 85 æfter wæl-nīðe wæcnan scolde. Þā se ellen-gǣst earfoðlīce þrāge geþolode, sē þe in þȳstrum bād, þæt hē dōgora gehwām drēam gehȳrde hlūdne in healle; þǣr wæs hearpan swēg, swutol sang scopes. Sægde sē þe cūðe frum-sceaft fīra feorran reccan",
                # the author has an ID where by authors can be disambiguated
                'author':{
                    'type':"author",
                    'id':"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                    'host':"http://127.0.0.1:5454/",
                    'displayName':"Lara Croft",
                    'url':"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                    'github': "http://github.com/laracroft"
                },
                'categories':["web","tutorial"],
                'count': 1023,
                'size': 50,
                'comments':[
                    {
                        'type':"comment",
                        'author':{
                            'type':"author",
                            # ID of the Author (UUID)
                            'id':"http://127.0.0.1:5454/author/1d698d25ff008f7538453c120f581471",
                            # url to the authors information
                            'url':"http://127.0.0.1:5454/author/1d698d25ff008f7538453c120f581471",
                            'host':"http://127.0.0.1:5454/",
                            "displayName":"Greg Johnson",
                            # HATEOS url for Github API
                            'github': "http://github.com/gjohnson"
                        },
                        'comment':"Sick Olde English",
                        'contentType':"text/markdown",
                        # ISO 8601 TIMESTAMP
                        'published':"2015-03-09T13:07:04+00:00",
                        # ID of the Comment (UUID)
                        'id':"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c",
                    }
                ],
                'published':"2015-03-09T13:07:04+00:00",
                'visibility':"PUBLIC",
                'unlisted': False,
            },
            {
                'type':"post",
                'title':"How to work on Django",
                'id':"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
                'source':"http://lastplaceigotthisfrom.com/posts/yyyyy",
                'origin':"http://heroku.com/posts/aaaa",
                'description':"This post discusses stuff -- brief",
                'contentType':"text/plain",
                'content':"Þā wæs on burgum Bēowulf Scyldinga, lēof lēod-cyning, longe þrāge folcum gefrǣge (fæder ellor hwearf, aldor of earde), oð þæt him eft onwōc hēah Healfdene; hēold þenden lifde, gamol and gūð-rēow, glæde Scyldingas. Þǣm fēower bearn forð-gerīmed in worold wōcun, weoroda rǣswan, Heorogār and Hrōðgār and Hālga til; hȳrde ic, þat Elan cwēn Ongenþēowes wæs Heaðoscilfinges heals-gebedde. Þā wæs Hrōðgāre here-spēd gyfen, wīges weorð-mynd, þæt him his wine-māgas georne hȳrdon, oð þæt sēo geogoð gewēox, mago-driht micel. Him on mōd bearn, þæt heal-reced hātan wolde, medo-ærn micel men gewyrcean, þone yldo bearn ǣfre gefrūnon, and þǣr on innan eall gedǣlan geongum and ealdum, swylc him god sealde, būton folc-scare and feorum gumena. Þā ic wīde gefrægn weorc gebannan manigre mǣgðe geond þisne middan-geard, folc-stede frætwan. Him on fyrste gelomp ǣdre mid yldum, þæt hit wearð eal gearo, heal-ærna mǣst; scōp him Heort naman, sē þe his wordes geweald wīde hæfde. Hē bēot ne ālēh, bēagas dǣlde, sinc æt symle. Sele hlīfade hēah and horn-gēap: heaðo-wylma bād, lāðan līges; ne wæs hit lenge þā gēn þæt se ecg-hete āðum-swerian 85 æfter wæl-nīðe wæcnan scolde. Þā se ellen-gǣst earfoðlīce þrāge geþolode, sē þe in þȳstrum bād, þæt hē dōgora gehwām drēam gehȳrde hlūdne in healle; þǣr wæs hearpan swēg, swutol sang scopes. Sægde sē þe cūðe frum-sceaft fīra feorran reccan",
                # the author has an ID where by authors can be disambiguated
                'author':{
                    'type':"author",
                    'id':"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                    'host':"http://127.0.0.1:5454/",
                    'displayName':"Craft Smith",
                    'url':"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                    'github': "http://github.com/laracroft"
                },
                'categories':["web","tutorial"],
                'count': 1023,
                'size': 50,
                'comments':[
                    {
                        'type':"comment",
                        'author':{
                            'type':"author",
                            # ID of the Author (UUID)
                            'id':"http://127.0.0.1:5454/author/1d698d25ff008f7538453c120f581471",
                            # url to the authors information
                            'url':"http://127.0.0.1:5454/author/1d698d25ff008f7538453c120f581471",
                            'host':"http://127.0.0.1:5454/",
                            "displayName":"Greg Johnson",
                            # HATEOS url for Github API
                            'github': "http://github.com/gjohnson"
                        },
                        'comment':"Sick Olde English",
                        'contentType':"text/markdown",
                        # ISO 8601 TIMESTAMP
                        'published':"2015-03-09T13:07:04+00:00",
                        # ID of the Comment (UUID)
                        'id':"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c",
                    }
                ],
                'published':"2012-03-09T13:07:04+00:00",
                'visibility':"PUBLIC",
                'unlisted': False,
            },
        ]
        
        return render(request, 'citrus_home/stream.html', {'json_list': mock_response})

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
# @login_required
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
        print(profile.user, profile.github,profile.displayName)
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
handles get requests with id and retrieve author profile information: username, displayname, github
handles post requests to state changes to author profile information: username, displayname, github 
Expected: POST - POST body = {"username": "new_username", "displayName": "new_displayName", "github":"new_github"} 
URL:/service/author/{AUTHOR_ID}
"""
# @login_required
def manage_profile(request, id):
    if request.method == 'GET':
        profile = get_object_or_404(CitrusAuthor, id=id)
        response = JsonResponse({'username': str(profile.user),
                                'displayName': str(profile.displayName),
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
            response.status_code = 418
            return response
    #not POST AND GET SO return sth else 
    else:
        response = JsonResponse({
            "message": "Method Not Allowed. Only support GET and POST"
        })

        response.status_code = 405
        return response

def setFormErrors(profile,new_username,new_displayName,new_github):
    u_valid = validate_username(profile, new_username)
    d_valid = validate_displayName(profile,new_displayName)
    g_valid = validate_github(profile,new_github)
    
    return [u_valid,d_valid,g_valid] 

def validate_fields(field_validities):
    print(field_validities)
    if False in field_validities:
        raise forms.ValidationError(u'one of three fields  are already in use.')
    else:
        return

def validate_username(profile, new_username):
    #cant query for username attributes from Citrus Author object
    if User.objects.filter(username=new_username).exists():
        existing_user = User.objects.get(username=new_username) 
        
        if  existing_user.id != profile.user.id:
            print("username is not available, someone who is not you has it")
            return False
            #raise forms.ValidationError(u'Username "%s" is already in use.' % new_username)
        else:
            print("you did not change your username - this one is already yours")
            return True
    else:
        print("username is available - no one had it yet")
        return True


def validate_displayName(profile, new_displayName):  
    if CitrusAuthor.objects.filter(displayName=new_displayName).exists():
        existing_user = CitrusAuthor.objects.get(displayName=new_displayName)
        if existing_user.id != profile.id:
            print("display name is not available, someone who is not you has it")
            return False
            #raise forms.ValidationError(u'Display Name "%s" is already in use.' % new_displayName)
        else:
            print("you did not change your display name - this one is already yours")
            return True
    else:
        print("display name is available - no one had it yet")
        return True

def validate_github(profile,  new_github):
   
    if CitrusAuthor.objects.filter(github=new_github).exists():
        existing_user = CitrusAuthor.objects.get(github=new_github)
        if existing_user.id != profile.id:
            print("github uri is not available, someone who is not you has it")
            return False
            #raise forms.ValidationError(u'github "%s" is already in use.' % new_github)
        else:
            print("you did not change your github uri - this one is already yours")
            return True
    else:
        print("github uri is available - no one had it yet")
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
handles GET request: get a list of authors who are their followers
format of list of followers: uuids separated by CONST_SEPARATOR
Expected: 
URL: ://service/author/{AUTHOR_ID}/followers
"""
# @login_required
def get_followers(request, author_id):
    if request.method == 'GET':
        # check for list of followers of author_id
        try:
            result = Follower.objects.get(uuid=author_id)
            print(result)
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

                # get the follower profile info
                author = CitrusAuthor.objects.get(id = uuid)
                
                json = {
                    "type": "Author",
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

        results = { "type": "followers",      
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
    DELETE: remove a follower
    PUT: Add a follower (must be authenticated)
    GET check if follower
Expected: 
URL: ://service/author/{AUTHOR_ID}/followers/{FOREIGN_AUTHOR_ID}
"""
# @login_required
@csrf_exempt
def edit_followers(request, author_id, foreign_author_id):
    # special case:
    if author_id == foreign_author_id:
        response = JsonResponse({"message":"author id and foreign author id are the same"})
        response.status_code = 400
        return response        
    elif request.method == 'DELETE':
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
        
        # remove that foreign id from the string
        followers = followers.replace(str(foreign_author_id),"")
        result.followers_uuid = followers
        result.save()

        response = JsonResponse({"results":"success"})
        response.status_code = 200
        return response
    elif request.method == 'PUT':
        # DO I VERIFY FOREIGN AUTHOR ID, I.E IF IT'S FROM OTHER SERVER ???

        # validate author id in citrus_author model:
        try:
            author = CitrusAuthor.objects.get(id=author_id)
        except ObjectDoesNotExist:
            response = JsonResponse({"results":"author_id doesnt exist"})
            response.status_code = 404
            return response

        # validate foregin id in model:
        try:
            foregin_id = CitrusAuthor.objects.get(id=foreign_author_id)
        except ObjectDoesNotExist:
            response = JsonResponse({"results":"invalid foreign id"})
            response.status_code = 404
            return response

        # validate author id in follower model
        try:
            result = Follower.objects.get(uuid=author_id)
        except ObjectDoesNotExist:
            # add foreign id 
            followers = str(foreign_author_id)
            # create instance of the follower with uuid to author_id
            new_follower_object = Follower(uuid = author,followers_uuid= followers)
            new_follower_object.save()
            print("created",new_follower_object.uuid)

            response = JsonResponse({"results":"success"})
            response.status_code = 200
            return response
        
        
        # add foreign id 
        followers = str(result.followers_uuid)+CONST_SEPARATOR+str(foreign_author_id)
        result.followers_uuid = followers
        result.save()

        response = JsonResponse({"results":"success"})
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
    POST author_id to follow foreign_author_id
Expected: 
URL: ://service/author/{AUTHOR_ID}/friendrequests/{FOREIGN_AUTHOR_ID}
"""
# @login_required
@csrf_exempt
def get_friend_requests(request, author_id):
    return None

"""
handles these requests:
    GET get all friends
Expected: 
URL: ://service/author/{AUTHOR_ID}/friends/
"""
# @login_required
# @csrf_exempt
def get_friends(request, author_id):
    if request.method == 'GET':
        # check for list of followers of author_id
        try:
            result = Friend.objects.get(uuid=author_id)
            print(result)
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

                # get the follower profile info
                author = CitrusAuthor.objects.get(id = uuid)
                
                json = {
                    "type": "Author",
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

        results = { "type": "friends",      
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
    DELETE: remove a friend
    GET check if friend
Expected: 
URL: ://service/author/{AUTHOR_ID}/friends/{FOREIGN_AUTHOR_ID}
"""
# @login_required
@csrf_exempt
def edit_friends(request, author_id, foreign_author_id):
    # special case:
    if author_id == foreign_author_id:
        response = JsonResponse({"message":"author id and foreign author id are the same"})
        response.status_code = 400
        return response        
    elif request.method == 'DELETE':
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
        
        # remove that foreign id from the string
        friends = friends.replace(str(foreign_author_id),"")
        result.friends_uuid = friends
        result.save()

        response = JsonResponse({"results":"success"})
        response.status_code = 200
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
    else:
        response = JsonResponse({"message":"Method not Allowed"})
        response.status_code = 405
        return response

