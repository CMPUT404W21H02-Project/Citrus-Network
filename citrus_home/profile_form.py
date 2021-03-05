from django import forms
 
# Form containing all editable profile information: username, displayName, github
class ProfileForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    displayName= forms.CharField(label='displayName', max_length=50)
    github= forms.CharField(label='github', max_length=200)

class ProfileFormError:

    def __init__(self, username, displayname, github):
        self.setUsernameError(username)
        self.setDisplayNameError(displayname)
        self.setGithubNameError(github)
    
    def setUsernameError(self,username):
        if username:
            self.usernameError = ""
        else:
            self.usernameError = "That username is taken. Try Again!"
    
    def setDisplayNameError(self,displayname):
        if displayname:
            self.displayNameError = ""
        else:
            self.displayNameError = "That display name is taken. Try Again!"
    
    def setGithubNameError(self,github):
        if github:
            self.githubNameError = ""
        else:
            self.githubNameError = "That Github is in use. Try Again!"

       
        








    

    
    