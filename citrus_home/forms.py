from django.forms import ModelForm
from django import forms
from .models import Post

TRUE_FALSE_CHOICES = (
    (True, 'Unlisted'),
    (False, 'Listed')
)

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'description', 'content', 'contentType', 'categories', 'visibility', 'unlisted', 'shared_with')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control','rows': 4}),
            'contentType': forms.Select(attrs={'class': 'form-control'}),
            'categories': forms.TextInput(attrs={'class': 'form-control'}),
            'visibility': forms.Select(attrs={'class': 'form-control'}),
            'unlisted': forms.Select(choices=TRUE_FALSE_CHOICES),
            'shared_with': forms.TextInput(attrs={'class': 'form-control'}),
        }