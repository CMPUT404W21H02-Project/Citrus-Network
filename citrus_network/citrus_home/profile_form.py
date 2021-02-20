from django import forms

class ProfileForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    displayName= forms.CharField(label='displayName', max_length=50)
    github= forms.CharField(label='github', max_length=200)