from django import forms

# Form containing all editable profile information: username, displayName, github
class ProfileForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    displayName= forms.CharField(label='displayName', max_length=50)
    github= forms.CharField(label='github', max_length=200)

class ProfileFormError():
    usernameError = "That username is taken. Try Again!"
    displayNameError = "That display name is taken. Try Again!"
    githubNameError = "That Github is in use. Try Again!"





    

    
    